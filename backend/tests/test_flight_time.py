import unittest

from app.services.biomechanics.flight_time import (
    estimate_duty_factor,
    estimate_flight_times,
)


class TestFlightTime(unittest.TestCase):
    def test_estimates_flight_time_between_contacts(self) -> None:
        contacts = {
            "left": [
                {
                    "contact_start_ms": 0,
                    "contact_end_ms": 100,
                },
                {
                    "contact_start_ms": 500,
                    "contact_end_ms": 600,
                },
            ],
            "right": [
                {
                    "contact_start_ms": 250,
                    "contact_end_ms": 350,
                },
            ],
        }

        result = estimate_flight_times(contacts)

        self.assertEqual(
            result["status"],
            "experimental",
        )
        self.assertEqual(
            result["events_used"],
            2,
        )
        self.assertEqual(
            result["median_flight_time_ms"],
            150.0,
        )

    def test_estimates_duty_factor(self) -> None:
        ground_contact = {
            "overall": {
                "median_contact_time_ms": 100.0,
            }
        }

        flight_time = {
            "median_flight_time_ms": 150.0,
        }

        result = estimate_duty_factor(
            ground_contact,
            flight_time,
        )

        self.assertEqual(
            result["duty_factor_percent"],
            40.0,
        )


if __name__ == "__main__":
    unittest.main()
