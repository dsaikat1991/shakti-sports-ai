import unittest

from app.services.biomechanics.running_cycle import (
    classify_cycle_phases,
    detect_running_cycles,
)


class TestRunningCycle(unittest.TestCase):
    def test_detects_same_side_stride_cycles(self) -> None:
        contacts = {
            "left": [
                {
                    "contact_start_ms": 0,
                    "contact_end_ms": 100,
                },
                {
                    "contact_start_ms": 600,
                    "contact_end_ms": 700,
                },
            ],
            "right": [
                {
                    "contact_start_ms": 300,
                    "contact_end_ms": 400,
                },
                {
                    "contact_start_ms": 900,
                    "contact_end_ms": 1000,
                },
            ],
        }

        result = detect_running_cycles(contacts)

        self.assertEqual(
            result["status"],
            "experimental",
        )
        self.assertEqual(
            result["cycles_used"],
            2,
        )
        self.assertEqual(
            result["median_stride_duration_ms"],
            600.0,
        )

    def test_phase_timeline_contains_contact_and_flight(self) -> None:
        contacts = {
            "left": [
                {
                    "contact_start_ms": 0,
                    "contact_end_ms": 100,
                }
            ],
            "right": [],
        }

        flight = {
            "events": [
                {
                    "start_ms": 100,
                    "end_ms": 250,
                }
            ]
        }

        result = classify_cycle_phases(
            contacts,
            flight,
        )

        phases = [
            item["phase"]
            for item in result["timeline"]
        ]

        self.assertIn("contact", phases)
        self.assertIn("flight", phases)


if __name__ == "__main__":
    unittest.main()
