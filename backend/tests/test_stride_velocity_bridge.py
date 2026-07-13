import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.pose_remote.stride_velocity_bridge import (
    build_foot_contact_events,
    build_stride_based_progression,
)


def landmark(x: float, y: float, *, confidence: float = 0.9) -> dict[str, float]:
    return {"x": x, "y": y, "visibility": confidence, "presence": confidence}


def make_frame(index: int, *, left_ankle_x: float, right_ankle_x: float) -> FrameMetrics:
    points = [landmark(0.5, 0.5) for _ in range(33)]

    # left leg: ankle(27), heel(29), toe(31); right leg: ankle(28), heel(30), toe(32)
    for joint_index in (27, 29, 31):
        points[joint_index] = landmark(left_ankle_x, 0.9)
    for joint_index in (28, 30, 32):
        points[joint_index] = landmark(right_ankle_x, 0.9)

    # torso landmarks so centre-of-mass estimation succeeds
    for joint_index in (11, 12, 13, 14, 15, 16, 23, 24, 25, 26):
        points[joint_index] = landmark(0.5, 0.5)

    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 20,
        joint_angles={},
        bounding_box=None,
        camera_view={"view": "Side View", "confidence": 90.0, "suitable_for_sprint": True},
        landmarks=tuple(points),
        backend="rtmpose",
    )


def make_contact_event(*, side: str, frame_index: int, timestamp_ms: int) -> dict:
    return {
        "side": side,
        "contact_start_ms": timestamp_ms,
        "contact_end_ms": timestamp_ms,
        "contact_time_ms": 60,
        "peak_frame_index": frame_index,
        "peak_timestamp_ms": timestamp_ms,
        "confidence": 90.0,
        "method": "foot_y_local_maximum_proxy",
    }


class TestBuildFootContactEvents(unittest.TestCase):
    def test_attaches_same_frame_leg_split(self) -> None:
        frames = [
            make_frame(0, left_ankle_x=0.40, right_ankle_x=0.55),
            make_frame(1, left_ankle_x=0.42, right_ankle_x=0.60),
        ]
        contact_events = {
            "left": [make_contact_event(side="left", frame_index=0, timestamp_ms=0)],
            "right": [make_contact_event(side="right", frame_index=1, timestamp_ms=20)],
        }

        contacts = build_foot_contact_events(contact_events, frames)

        self.assertEqual(len(contacts), 2)
        left_contact = next(c for c in contacts if c.side == "left")
        right_contact = next(c for c in contacts if c.side == "right")

        # leg_split compares both feet within the SAME frame as the contact.
        self.assertAlmostEqual(left_contact.leg_split, abs(0.40 - 0.55), places=6)
        self.assertAlmostEqual(right_contact.leg_split, abs(0.60 - 0.42), places=6)

    def test_skips_events_with_no_matching_frame(self) -> None:
        frames = [make_frame(0, left_ankle_x=0.40, right_ankle_x=0.55)]
        contact_events = {
            "left": [make_contact_event(side="left", frame_index=99, timestamp_ms=0)],
            "right": [],
        }

        contacts = build_foot_contact_events(contact_events, frames)

        self.assertEqual(contacts, [])


class TestBuildStrideBasedProgression(unittest.TestCase):
    def test_progression_is_monotonically_increasing(self) -> None:
        frames = [
            make_frame(0, left_ankle_x=0.50, right_ankle_x=0.52),
            make_frame(1, left_ankle_x=0.50, right_ankle_x=0.60),
            make_frame(2, left_ankle_x=0.50, right_ankle_x=0.65),
        ]
        contact_events = {
            "left": [],
            "right": [
                make_contact_event(side="right", frame_index=0, timestamp_ms=0),
                make_contact_event(side="right", frame_index=1, timestamp_ms=20),
                make_contact_event(side="right", frame_index=2, timestamp_ms=40),
            ],
        }
        contacts = build_foot_contact_events(contact_events, frames)

        timestamps_ms, progression = build_stride_based_progression(contacts, side="right")

        self.assertEqual(timestamps_ms, [0, 20, 40])
        self.assertEqual(len(progression), 3)
        self.assertTrue(all(b >= a for a, b in zip(progression, progression[1:])))

    def test_filters_to_requested_side_only(self) -> None:
        frames = [
            make_frame(0, left_ankle_x=0.30, right_ankle_x=0.50),
            make_frame(1, left_ankle_x=0.35, right_ankle_x=0.55),
        ]
        contact_events = {
            "left": [make_contact_event(side="left", frame_index=0, timestamp_ms=0)],
            "right": [make_contact_event(side="right", frame_index=1, timestamp_ms=20)],
        }
        contacts = build_foot_contact_events(contact_events, frames)

        timestamps_ms, progression = build_stride_based_progression(contacts, side="right")

        self.assertEqual(timestamps_ms, [20])
        self.assertEqual(len(progression), 1)

    def test_empty_contacts_return_empty_series(self) -> None:
        timestamps_ms, progression = build_stride_based_progression([], side="right")

        self.assertEqual(timestamps_ms, [])
        self.assertEqual(progression, [])


if __name__ == "__main__":
    unittest.main()
