import unittest

from app.services.biomechanics.cadence import (
    estimate_cadence_from_knee_events,
)


class TestCadence(unittest.TestCase):
    def test_estimates_cadence_from_peak_flexion_events(self) -> None:
        events = {
            "left": [
                {
                    "event": "peak_flexion",
                    "timestamp_ms": 0,
                },
                {
                    "event": "peak_flexion",
                    "timestamp_ms": 600,
                },
            ],
            "right": [
                {
                    "event": "peak_flexion",
                    "timestamp_ms": 300,
                },
                {
                    "event": "peak_flexion",
                    "timestamp_ms": 900,
                },
            ],
        }

        result = estimate_cadence_from_knee_events(events)

        self.assertEqual(result["status"], "experimental")
        self.assertEqual(
            result["estimated_steps_per_minute"],
            200.0,
        )

    def test_reports_insufficient_data(self) -> None:
        result = estimate_cadence_from_knee_events(
            {
                "left": [],
                "right": [],
            }
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )
        self.assertIsNone(
            result["estimated_steps_per_minute"]
        )


if __name__ == "__main__":
    unittest.main()
