import unittest

from app.services.sprint.phase_detector import (
    detect_sprint_phases_v2,
)
from app.services.sprint.phase_models import (
    SprintSignalFrame,
)
from app.services.sprint.sprint_intelligence import (
    analyze_sprint_intelligence_v2,
)


def build_frames() -> list[SprintSignalFrame]:
    velocities = [
        0.0,
        0.2,
        0.6,
        1.2,
        2.0,
        3.0,
        4.2,
        5.4,
        6.4,
        7.1,
        7.6,
        7.9,
        8.0,
        8.0,
        7.9,
        7.7,
        7.3,
        6.8,
    ]

    frames = []

    previous_velocity = velocities[0]

    for index, velocity in enumerate(velocities):
        acceleration = (
            velocity - previous_velocity
        ) / 0.1 if index > 0 else 0.0

        torso = min(
            88.0,
            28.0 + index * 4.0,
        )

        frames.append(
            SprintSignalFrame(
                frame_index=index,
                timestamp_ms=index * 100,
                com_position_x=index * 0.1,
                com_velocity_x=velocity,
                com_acceleration_x=acceleration,
                torso_angle_deg=torso,
                cadence_spm=250.0 + index * 2.0,
                ground_contact_ms=max(
                    90.0,
                    170.0 - index * 5.0,
                ),
                flight_time_ms=min(
                    130.0,
                    60.0 + index * 4.0,
                ),
                confidence=0.95,
            )
        )

        previous_velocity = velocity

    return frames


class TestSprintIntelligenceV20Phase1(
    unittest.TestCase
):
    def test_phase_detector_returns_segments(self) -> None:
        result = detect_sprint_phases_v2(
            build_frames()
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertGreater(
            len(result["segments"]),
            0,
        )

        phases = {
            item["phase"]
            for item in result["phase_frames"]
        }

        self.assertIn(
            "drive",
            phases,
        )

        self.assertIn(
            "maximum_velocity",
            phases,
        )

    def test_full_intelligence_contains_phase_metrics(self) -> None:
        result = analyze_sprint_intelligence_v2(
            build_frames()
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertEqual(
            result["engine_version"],
            "2.0.0-phase1",
        )

        self.assertIn(
            "phases",
            result["phase_metrics"],
        )

    def test_short_sequence_is_rejected(self) -> None:
        result = detect_sprint_phases_v2(
            build_frames()[:4]
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )


if __name__ == "__main__":
    unittest.main()
