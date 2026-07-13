import unittest

from app.services.biomechanics.gait_event_evaluator import (
    evaluate_by_event_type,
    evaluate_events,
)
from app.services.biomechanics.gait_event_models import (
    GaitEvent,
)


class TestGaitEventEvaluator(unittest.TestCase):
    def test_perfect_match(self) -> None:
        actual = [
            GaitEvent(
                event_type="initial_contact",
                side="left",
                timestamp_ms=1000,
            ),
            GaitEvent(
                event_type="toe_off",
                side="left",
                timestamp_ms=1120,
            ),
        ]

        predicted = [
            GaitEvent(
                event_type="initial_contact",
                side="left",
                timestamp_ms=1010,
            ),
            GaitEvent(
                event_type="toe_off",
                side="left",
                timestamp_ms=1110,
            ),
        ]

        result = evaluate_events(
            predicted,
            actual,
            tolerance_ms=30,
        )

        self.assertEqual(
            result["f1_score"],
            1.0,
        )
        self.assertEqual(
            result["timing_error_ms"]["mean_absolute_error"],
            10.0,
        )

    def test_wrong_side_does_not_match(self) -> None:
        actual = [
            GaitEvent(
                event_type="initial_contact",
                side="left",
                timestamp_ms=1000,
            )
        ]

        predicted = [
            GaitEvent(
                event_type="initial_contact",
                side="right",
                timestamp_ms=1000,
            )
        ]

        result = evaluate_events(
            predicted,
            actual,
            tolerance_ms=50,
        )

        self.assertEqual(
            result["counts"]["true_positives"],
            0,
        )
        self.assertEqual(
            result["counts"]["false_positives"],
            1,
        )
        self.assertEqual(
            result["counts"]["false_negatives"],
            1,
        )

    def test_reports_each_event_type(self) -> None:
        result = evaluate_by_event_type(
            predicted=[],
            actual=[],
        )

        self.assertIn(
            "initial_contact",
            result,
        )
        self.assertIn(
            "toe_off",
            result,
        )


if __name__ == "__main__":
    unittest.main()
