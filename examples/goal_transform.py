"""Minimal GoalPoint world-to-local conversion used by the public demo."""

from __future__ import annotations

import math


def world_goal_to_local(robot_xy: tuple[float, float], robot_yaw: float, goal_xy: tuple[float, float]):
    dx = goal_xy[0] - robot_xy[0]
    dy = goal_xy[1] - robot_xy[1]
    cos_yaw = math.cos(robot_yaw)
    sin_yaw = math.sin(robot_yaw)
    forward = cos_yaw * dx + sin_yaw * dy
    left = -sin_yaw * dx + cos_yaw * dy
    return forward, left


if __name__ == "__main__":
    print(world_goal_to_local((1.0, 2.0), math.radians(90), (1.0, 5.0)))
