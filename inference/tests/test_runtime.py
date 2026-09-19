import math
import unittest

from inference.runtime import (
    GoalPointSession,
    ModelOutput,
    Pose,
    WorldPoint,
    model_local_point,
    sampled_indices,
    world_goal_to_episode,
)


class FakeImage:
    def __init__(self, size=(640, 569)):
        self.width, self.height = size

    def resize(self, size):
        return FakeImage(size)


class FakeBackend:
    def __init__(self, logits=None):
        self.logits = logits or [-1.0] * 5
        self.calls = []

    def predict(self, images, prompt, input_waypoints):
        self.calls.append((images, prompt, input_waypoints))
        return ModelOutput([[0.2, 0.5]] * 5, self.logits, [0.0] * 5)


class RuntimeTests(unittest.TestCase):
    def test_world_to_episode_heading(self):
        origin = WorldPoint(0, 0, 0)
        self.assertAlmostEqual(world_goal_to_episode(WorldPoint(0, 0, -3), origin, 0).x, 3)
        self.assertAlmostEqual(world_goal_to_episode(WorldPoint(-3, 0, 0), origin, math.pi / 2).x, 3)

    def test_local_goal_axes_and_scale(self):
        side, forward = model_local_point(Pose(0, 0, 0), Pose(3, 1, 0))
        self.assertAlmostEqual(side, -1 / 0.3)
        self.assertAlmostEqual(forward, 3 / 0.3)
        side, forward = model_local_point(Pose(0, 0, math.pi / 2), Pose(3, 1, 0))
        self.assertAlmostEqual(side, 3 / 0.3)
        self.assertAlmostEqual(forward, 1 / 0.3)

    def test_three_views_and_moving_goal_input(self):
        backend = FakeBackend()
        start, goal = WorldPoint(0, 0, 0), WorldPoint(0, 0, -6)
        session = GoalPointSession(backend, start, 0, goal)
        first = session.step(front=FakeImage(), pose=Pose(0, 0, 0), instruction="Reach the goal")
        second = session.step(front=FakeImage(), pose=Pose(3, 0, 0), instruction="Reach the goal")
        self.assertEqual(len(backend.calls[0][0]), 23)
        self.assertEqual(len(first.input_waypoints), 6)
        self.assertEqual(first.image_indices, [0] * 21)
        self.assertAlmostEqual(first.input_waypoints[-1][1], 20)
        self.assertAlmostEqual(second.input_waypoints[-1][1], 10)
        self.assertEqual(session.goal, goal)
        self.assertEqual(first.trajectory[0], [0.5, -0.2, 0.0])
        self.assertIn("<input_target>", backend.calls[0][1])
        self.assertFalse(second.stop)

    def test_stop_and_reset(self):
        backend = FakeBackend([0.1] * 5)
        session = GoalPointSession(backend, WorldPoint(0, 0, 0), 0, WorldPoint(0, 0, -1),
                                   num_views=1, stop_consecutive=2)
        self.assertFalse(session.step(front=FakeImage(), pose=Pose(0, 0, 0), instruction="Stop").stop)
        self.assertTrue(session.step(front=FakeImage(), pose=Pose(0, 0, 0), instruction="Stop").stop)
        with self.assertRaises(RuntimeError):
            session.step(front=FakeImage(), pose=Pose(0, 0, 0), instruction="Stop")
        session.reset()
        self.assertFalse(session.done)
        self.assertEqual(len(session.front_history), 0)
        self.assertEqual(len(sampled_indices(4, 4)), 4)
        self.assertEqual(len(backend.calls[0][0]), 21)


if __name__ == "__main__":
    unittest.main()
