"""Episode-local Goal Point inference used by the online evaluation bridge.

Images are PIL-compatible objects. The backend is injected so this module can
be tested without model weights, CUDA, Habitat, or a private HTTP service.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol


PREDICT_SCALE = 0.3
HISTORY_FRAMES = 20
IMAGE_SIZE = (640, 569)
HISTORY_SIZE = (160, 142)

PROMPT_FRONT = """You are an autonomous navigation robot. You will get a task with historical pictures and the current picture you see.
Based on this information, decide the next 5 local waypoints. If you finish your mission, output <|stop|>.
# Your historical pictures are: {history_img_string}
# Your current observation is frontside: {front_image}
# Historical trajectory coordinates are: <input_pos1><input_pos2><input_pos3><input_pos4>
# Current observation coordinate is: <input_pos5>
# Goal guidance coordinate is: <input_target>
# Your mission is: {instruction} <|NAV|>
Output the waypoint"""

PROMPT_THREE = """You are an autonomous navigation robot. You will get a task with historical pictures and current pictures you see.
Based on this information, decide the next 5 local waypoints. If you finish your mission, output <|stop|>.
# Your historical pictures are: {history_img_string}
# Your current observations is leftside: {left_image}, frontside: {front_image}, rightside: {right_image}
# Historical trajectory coordinates are: <input_pos1><input_pos2><input_pos3><input_pos4>
# Current observation coordinate is: <input_pos5>
# Goal guidance coordinate is: <input_target>
# Your mission is: {instruction} <|NAV|>
Output the waypoint"""


@dataclass(frozen=True)
class Pose:
    x: float  # Episode odom forward, metres
    y: float  # Episode odom left, metres
    yaw: float  # Radians from the episode start heading


@dataclass(frozen=True)
class WorldPoint:
    x: float
    y: float
    z: float


@dataclass
class ModelOutput:
    waypoints: list[list[float]]  # Metres, model [side, forward] convention
    arrive_logits: list[float]
    heading_angles: list[float]


@dataclass
class StepResult:
    input_waypoints: list[list[float]]
    image_indices: list[int]
    trajectory: list[list[float]]  # Robot-local [forward, left, heading]
    arrive_logits: list[float]
    stop: bool


class Backend(Protocol):
    def predict(self, images: list[Any], prompt: str, input_waypoints: list[list[float]]) -> ModelOutput: ...


def sampled_indices(end_index: int, count: int) -> list[int]:
    if end_index <= 0:
        return [0] * count
    if count == 1:
        return [end_index]
    return [round(i * end_index / (count - 1)) for i in range(count)]


def world_goal_to_episode(goal: WorldPoint, start: WorldPoint, start_yaw: float) -> Pose:
    """Project Habitat world X/Z onto the start-frame forward/left axes."""
    dx, dz = goal.x - start.x, goal.z - start.z
    forward = -math.sin(start_yaw) * dx - math.cos(start_yaw) * dz
    left = -math.cos(start_yaw) * dx + math.sin(start_yaw) * dz
    return Pose(forward, left, 0.0)


def model_local_point(robot: Pose, target: Pose) -> list[float]:
    """Return [model side, model forward] divided by the training scale."""
    dx, dy = target.x - robot.x, target.y - robot.y
    side = math.sin(robot.yaw) * dx - math.cos(robot.yaw) * dy
    forward = math.cos(robot.yaw) * dx + math.sin(robot.yaw) * dy
    return [side / PREDICT_SCALE, forward / PREDICT_SCALE]


class GoalPointSession:
    def __init__(
        self,
        backend: Backend,
        start: WorldPoint,
        start_yaw: float,
        goal: WorldPoint,
        *,
        num_views: int = 3,
        stop_logit_threshold: float = 0.0,
        stop_consecutive: int = 1,
    ) -> None:
        if num_views not in (1, 3):
            raise ValueError("num_views must be 1 or 3")
        if stop_consecutive < 1:
            raise ValueError("stop_consecutive must be positive")
        self.backend = backend
        self.start = start
        self.goal = goal
        self.goal_episode = world_goal_to_episode(goal, start, start_yaw)
        self.num_views = num_views
        self.stop_logit_threshold = stop_logit_threshold
        self.stop_consecutive = stop_consecutive
        self.reset()

    def reset(self) -> None:
        self.front_history: list[Any] = []
        self.left_history: list[Any] = []
        self.right_history: list[Any] = []
        self.pose_history: list[Pose] = []
        self.stop_streak = 0
        self.done = False

    def step(
        self,
        *,
        front: Any,
        pose: Pose,
        instruction: str,
        left: Any | None = None,
        right: Any | None = None,
    ) -> StepResult:
        if self.done:
            raise RuntimeError("Episode has stopped; reset before another inference")
        if not instruction.strip():
            raise ValueError("instruction is required")
        self.front_history.append(front.resize(IMAGE_SIZE))
        self.left_history.append((left or front).resize(IMAGE_SIZE))
        self.right_history.append((right or front).resize(IMAGE_SIZE))
        self.pose_history.append(pose)

        current = len(self.pose_history) - 1
        history_end = max(0, current - 1)
        history_indices = sampled_indices(history_end, HISTORY_FRAMES)
        images = [self.front_history[i].resize(HISTORY_SIZE) for i in history_indices]
        if self.num_views == 3:
            images.extend((self.left_history[current], self.front_history[current], self.right_history[current]))
        else:
            images.append(self.front_history[current])

        odom_indices = sampled_indices(history_end, 4) + [current]
        input_waypoints = [model_local_point(pose, self.pose_history[i]) for i in odom_indices]
        input_waypoints.append(model_local_point(pose, self.goal_episode))
        prompt = (PROMPT_THREE if self.num_views == 3 else PROMPT_FRONT).format(
            history_img_string="", left_image="", front_image="", right_image="",
            instruction=instruction.strip(),
        )
        output = self.backend.predict(images, prompt, input_waypoints)

        candidate = len(output.arrive_logits) >= 5 and all(
            value >= self.stop_logit_threshold for value in output.arrive_logits[:5]
        )
        self.stop_streak = self.stop_streak + 1 if candidate else 0
        self.done = self.stop_streak >= self.stop_consecutive
        trajectory = [
            [float(point[1]), -float(point[0]), float(output.heading_angles[i])]
            for i, point in enumerate(output.waypoints)
        ]
        return StepResult(
            input_waypoints=input_waypoints,
            image_indices=history_indices + [current],
            trajectory=trajectory,
            arrive_logits=output.arrive_logits,
            stop=self.done,
        )
