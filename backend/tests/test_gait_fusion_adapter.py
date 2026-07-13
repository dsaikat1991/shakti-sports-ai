import unittest

from app.services.biomechanics.gait_fusion_adapter import (
    build_contact_candidate,
    build_toe_off_candidate,
    resolve_candidates,
)


class TestGaitFusionAdapter(unittest.TestCase):
    def test_contact_and_toe_off_sequence(self) -> None:
        reliability = {
            "foot": 0.95,
            "ankle": 0.95,
            "knee": 0.90,
            "hip": 0.90,
            "com": 0.90,
        }

        contact = build_contact_candidate(
            side="left",
            timestamp_ms=1000,
            frame_index=30,
            signals={
                "foot_low": 0.95,
                "foot_speed": 0.10,
                "ankle_acceleration": 0.90,
                "knee_extension": 0.80,
                "com_stability": 0.85,
            },
            reliability=reliability,
        )

        toe_off = build_toe_off_candidate(
            side="left",
            timestamp_ms=1120,
            frame_index=34,
            signals={
                "foot_upward_velocity": 0.95,
                "foot_speed": 0.90,
                "ankle_acceleration": 0.85,
                "knee_angular_speed": 0.80,
                "hip_velocity": 0.70,
            },
            reliability=reliability,
        )

        result = resolve_candidates(
            [contact, toe_off]
        )

        self.assertEqual(
            result["status"],
            "completed",
        )
        self.assertEqual(
            len(result["events"]),
            2,
        )


if __name__ == "__main__":
    unittest.main()
