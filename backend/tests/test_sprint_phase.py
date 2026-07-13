import unittest

from app.services.athletics.sprint_phase import (
    detect_sprint_phases,
)


class TestSprintPhaseDetection(unittest.TestCase):
    def test_detects_coarse_phases(self) -> None:
        timestamps = [
            index * 100
            for index in range(20)
        ]

        progression = [
            0.00,
            0.02,
            0.06,
            0.12,
            0.20,
            0.30,
            0.42,
            0.55,
            0.68,
            0.80,
            0.91,
            1.01,
            1.10,
            1.18,
            1.25,
            1.31,
            1.36,
            1.40,
            1.42,
            1.43,
        ]

        result = detect_sprint_phases(
            timestamps_ms=timestamps,
            horizontal_progression=progression,
        )

        self.assertIn(
            result["status"],
            ("experimental", "insufficient_data"),
        )

        self.assertGreater(
            len(result["derived_signals"]["velocity"]),
            0,
        )

    def test_rejects_short_sequence(self) -> None:
        result = detect_sprint_phases(
            timestamps_ms=[0, 100, 200],
            horizontal_progression=[
                0.0,
                0.1,
                0.2,
            ],
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )


if __name__ == "__main__":
    unittest.main()
