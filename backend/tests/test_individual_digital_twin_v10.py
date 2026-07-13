import unittest

from app.services.digital_twin_v2.baseline import (
    build_personal_baselines,
)
from app.services.digital_twin_v2.engine import (
    build_individual_digital_twin,
)
from app.services.digital_twin_v2.intervention import (
    evaluate_intervention_response,
)
from app.services.digital_twin_v2.models import (
    TwinSession,
)
from app.services.digital_twin_v2.repository import (
    InMemoryDigitalTwinRepository,
)


def session(
    index: int,
    *,
    efficiency: float,
    contact: float,
    cadence: float,
    symmetry: float,
    economy: float,
    intervention_id: str | None = None,
) -> TwinSession:
    context = {}

    if intervention_id is not None:
        context[
            "intervention_id"
        ] = intervention_id

    return TwinSession(
        athlete_id="athlete-1",
        performance_id=f"performance-{index}",
        session_id=f"session-{index}",
        event="sprint",
        recorded_at=(
            f"2026-07-{index + 1:02d}T10:00:00"
        ),
        features={
            "mechanical_efficiency_score": (
                efficiency
            ),
            "horizontal_force_score": (
                efficiency - 1.0
            ),
            "net_propulsion_score": (
                efficiency - 2.0
            ),
            "stride_geometry_score": (
                efficiency - 3.0
            ),
            "foot_trajectory_score": (
                efficiency - 4.0
            ),
            "leg_spring_score": (
                efficiency - 2.5
            ),
            "sprint_economy_score": economy,
            "arm_mechanics_score": (
                efficiency - 5.0
            ),
            "pelvis_trunk_score": (
                efficiency - 4.5
            ),
            "max_velocity_maintenance_score": (
                efficiency - 1.5
            ),
            "symmetry_score": symmetry,
            "ground_contact_ms": contact,
            "cadence_spm": cadence,
        },
        confidences={
            "mechanical_efficiency_score": 0.92,
            "ground_contact_ms": 0.90,
            "cadence_spm": 0.91,
            "symmetry_score": 0.89,
            "sprint_economy_score": 0.91,
        },
        context=context,
    )


class TestIndividualDigitalTwinV10(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.sessions = [
            session(
                0,
                efficiency=72.0,
                contact=139.0,
                cadence=270.0,
                symmetry=82.0,
                economy=70.0,
            ),
            session(
                1,
                efficiency=75.0,
                contact=136.0,
                cadence=273.0,
                symmetry=84.0,
                economy=73.0,
            ),
            session(
                2,
                efficiency=78.0,
                contact=132.0,
                cadence=277.0,
                symmetry=87.0,
                economy=77.0,
                intervention_id="wicket-drills",
            ),
            session(
                3,
                efficiency=82.0,
                contact=127.0,
                cadence=281.0,
                symmetry=90.0,
                economy=81.0,
                intervention_id="wicket-drills",
            ),
            session(
                4,
                efficiency=85.0,
                contact=122.0,
                cadence=285.0,
                symmetry=92.0,
                economy=84.0,
                intervention_id="wicket-drills",
            ),
        ]

    def test_repository(self) -> None:
        repository = (
            InMemoryDigitalTwinRepository()
        )

        repository.save_many(
            self.sessions
        )

        self.assertEqual(
            len(
                repository.history(
                    athlete_id="athlete-1",
                    event="sprint",
                )
            ),
            5,
        )

        self.assertEqual(
            repository.latest(
                athlete_id="athlete-1",
            ).performance_id,
            "performance-4",
        )

    def test_baseline(self) -> None:
        result = build_personal_baselines(
            self.sessions
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertIn(
            "mechanical_efficiency_score",
            result["features"],
        )

    def test_intervention_response(self) -> None:
        result = (
            evaluate_intervention_response(
                self.sessions
            )
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertEqual(
            len(
                result["interventions"]
            ),
            1,
        )

    def test_full_twin(self) -> None:
        result = (
            build_individual_digital_twin(
                self.sessions
            )
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        twin = result["digital_twin"]

        self.assertEqual(
            twin["sessions_analyzed"],
            5,
        )

        self.assertIn(
            "mechanical_efficiency_score",
            twin["identity_vector"],
        )

        self.assertIn(
            "readiness",
            twin,
        )

        self.assertIn(
            "adaptations",
            twin,
        )

    def test_requires_minimum_history(self) -> None:
        result = (
            build_individual_digital_twin(
                self.sessions[:2]
            )
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )


if __name__ == "__main__":
    unittest.main()
