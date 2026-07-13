import unittest

from app.services.digital_twin.fatigue import (
    detect_longitudinal_fatigue_pattern,
)
from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
)
from app.services.digital_twin.personal_bests import (
    find_personal_best,
)
from app.services.digital_twin.plateau import (
    detect_plateau,
)
from app.services.digital_twin.store import (
    InMemoryDigitalTwinStore,
)
from app.services.digital_twin.summary import (
    build_digital_twin_summary,
)
from app.services.digital_twin.trends import (
    analyze_metric_trend,
)


def snapshot(
    index: int,
    *,
    efficiency: float,
    contact: float,
    cadence: float,
    symmetry: float,
) -> AthleteMetricSnapshot:
    return AthleteMetricSnapshot(
        athlete_id="athlete-1",
        performance_id=f"performance-{index}",
        session_id=f"session-{index}",
        event="sprint",
        recorded_at=(
            f"2026-06-{index + 1:02d}T10:00:00"
        ),
        metrics={
            "mechanical_efficiency_score": (
                efficiency
            ),
            "front_side_score": (
                efficiency - 2.0
            ),
            "back_side_score": (
                efficiency - 4.0
            ),
            "ground_contact_ms": contact,
            "cadence_spm": cadence,
            "symmetry_score": symmetry,
            "vertical_oscillation_percent": 7.0,
            "push_off_completion_score": (
                efficiency - 5.0
            ),
        },
        confidences={
            "mechanical_efficiency_score": 0.91,
            "ground_contact_ms": 0.90,
            "cadence_spm": 0.92,
            "symmetry_score": 0.89,
        },
    )


class TestAthleteDigitalTwinV1(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.snapshots = [
            snapshot(
                0,
                efficiency=72.0,
                contact=140.0,
                cadence=270.0,
                symmetry=82.0,
            ),
            snapshot(
                1,
                efficiency=76.0,
                contact=135.0,
                cadence=274.0,
                symmetry=85.0,
            ),
            snapshot(
                2,
                efficiency=80.0,
                contact=130.0,
                cadence=278.0,
                symmetry=88.0,
            ),
            snapshot(
                3,
                efficiency=84.0,
                contact=124.0,
                cadence=282.0,
                symmetry=91.0,
            ),
            snapshot(
                4,
                efficiency=87.0,
                contact=120.0,
                cadence=286.0,
                symmetry=93.0,
            ),
        ]

    def test_store_and_history(
        self,
    ) -> None:
        store = InMemoryDigitalTwinStore()
        store.write_many(
            self.snapshots
        )

        history = store.athlete_history(
            athlete_id="athlete-1",
            event="sprint",
        )

        self.assertEqual(
            len(history),
            5,
        )

        self.assertEqual(
            store.latest_snapshot(
                athlete_id="athlete-1"
            ).performance_id,
            "performance-4",
        )

    def test_trend_detects_improvement(
        self,
    ) -> None:
        result = analyze_metric_trend(
            self.snapshots,
            metric_name=(
                "mechanical_efficiency_score"
            ),
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertEqual(
            result["trend"][
                "direction"
            ],
            "improving",
        )

    def test_lower_is_better_trend(
        self,
    ) -> None:
        result = analyze_metric_trend(
            self.snapshots,
            metric_name=(
                "ground_contact_ms"
            ),
        )

        self.assertEqual(
            result["trend"][
                "direction"
            ],
            "improving",
        )

    def test_personal_best(
        self,
    ) -> None:
        result = find_personal_best(
            self.snapshots,
            metric_name=(
                "ground_contact_ms"
            ),
        )

        self.assertEqual(
            result[
                "personal_best"
            ]["value"],
            120.0,
        )

    def test_plateau_detection(
        self,
    ) -> None:
        plateau_snapshots = [
            snapshot(
                index,
                efficiency=value,
                contact=120.0,
                cadence=286.0,
                symmetry=93.0,
            )
            for index, value
            in enumerate(
                [
                    84.0,
                    84.2,
                    84.1,
                    84.2,
                ]
            )
        ]

        result = detect_plateau(
            plateau_snapshots,
            metric_name=(
                "mechanical_efficiency_score"
            ),
        )

        self.assertTrue(
            result["plateau"]
        )

    def test_fatigue_pattern(
        self,
    ) -> None:
        history = [
            snapshot(
                0,
                efficiency=86.0,
                contact=120.0,
                cadence=286.0,
                symmetry=93.0,
            ),
            snapshot(
                1,
                efficiency=87.0,
                contact=119.0,
                cadence=287.0,
                symmetry=94.0,
            ),
            snapshot(
                2,
                efficiency=78.0,
                contact=132.0,
                cadence=274.0,
                symmetry=84.0,
            ),
            snapshot(
                3,
                efficiency=77.0,
                contact=134.0,
                cadence=272.0,
                symmetry=83.0,
            ),
            snapshot(
                4,
                efficiency=76.0,
                contact=136.0,
                cadence=270.0,
                symmetry=82.0,
            ),
        ]

        result = (
            detect_longitudinal_fatigue_pattern(
                history
            )
        )

        self.assertTrue(
            result[
                "pattern_detected"
            ]
        )

    def test_summary(
        self,
    ) -> None:
        result = build_digital_twin_summary(
            self.snapshots
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertEqual(
            result[
                "sessions_analyzed"
            ],
            5,
        )

        self.assertIn(
            "personal_bests",
            result,
        )


if __name__ == "__main__":
    unittest.main()
