import unittest

from app.services.athlete_intelligence.consistency import (
    analyze_consistency,
)
from app.services.athlete_intelligence.engine import (
    analyze_athlete_intelligence,
)
from app.services.athlete_intelligence.fatigue import (
    detect_fatigue_signature,
)
from app.services.athlete_intelligence.fingerprint import (
    build_biomechanical_fingerprint,
)
from app.services.athlete_intelligence.models import (
    AthleteSessionProfile,
)
from app.services.athlete_intelligence.trainability import (
    calculate_trainability_index,
)


def session(
    index: int,
    *,
    efficiency: float,
    contact: float,
    cadence: float,
    symmetry: float,
    economy: float,
) -> AthleteSessionProfile:
    return AthleteSessionProfile(
        athlete_id="athlete-1",
        performance_id=f"performance-{index}",
        recorded_at=(
            f"2026-07-{index + 1:02d}T10:00:00"
        ),
        event="sprint",
        features={
            "mechanical_efficiency_score": efficiency,
            "horizontal_force_score": efficiency - 1.0,
            "net_propulsion_score": efficiency - 2.0,
            "stride_geometry_score": efficiency - 3.0,
            "foot_trajectory_score": efficiency - 4.0,
            "leg_spring_score": efficiency - 2.5,
            "sprint_economy_score": economy,
            "arm_mechanics_score": efficiency - 5.0,
            "pelvis_trunk_score": efficiency - 4.5,
            "max_velocity_maintenance_score": efficiency - 1.5,
            "symmetry_score": symmetry,
            "ground_contact_ms": contact,
            "cadence_spm": cadence,
        },
        confidences={
            "mechanical_efficiency_score": 0.92,
            "sprint_economy_score": 0.91,
            "ground_contact_ms": 0.90,
            "cadence_spm": 0.91,
            "symmetry_score": 0.89,
        },
    )


class TestAthleteIntelligencePhaseAV01(unittest.TestCase):
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
            ),
            session(
                3,
                efficiency=82.0,
                contact=127.0,
                cadence=281.0,
                symmetry=90.0,
                economy=81.0,
            ),
            session(
                4,
                efficiency=85.0,
                contact=122.0,
                cadence=285.0,
                symmetry=92.0,
                economy=84.0,
            ),
        ]

        self.percentiles = {
            "mechanical_efficiency_score": 86.0,
            "horizontal_force_score": 82.0,
            "net_propulsion_score": 78.0,
            "stride_geometry_score": 72.0,
            "foot_trajectory_score": 64.0,
            "leg_spring_score": 80.0,
            "sprint_economy_score": 84.0,
            "arm_mechanics_score": 42.0,
            "pelvis_trunk_score": 38.0,
            "max_velocity_maintenance_score": 88.0,
            "symmetry_score": 90.0,
            "ground_contact_ms": 81.0,
            "cadence_spm": 79.0,
        }

    def test_fingerprint(self) -> None:
        result = build_biomechanical_fingerprint(
            self.sessions
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertGreater(
            len(
                result[
                    "fingerprint"
                ]["vector"]
            ),
            5,
        )

    def test_consistency(self) -> None:
        result = analyze_consistency(
            self.sessions
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertIsNotNone(
            result[
                "overall_consistency_score"
            ]
        )

    def test_fatigue_signature(self) -> None:
        fatigued = [
            session(
                0,
                efficiency=86.0,
                contact=120.0,
                cadence=286.0,
                symmetry=93.0,
                economy=85.0,
            ),
            session(
                1,
                efficiency=87.0,
                contact=119.0,
                cadence=287.0,
                symmetry=94.0,
                economy=86.0,
            ),
            session(
                2,
                efficiency=78.0,
                contact=131.0,
                cadence=274.0,
                symmetry=84.0,
                economy=76.0,
            ),
            session(
                3,
                efficiency=77.0,
                contact=133.0,
                cadence=272.0,
                symmetry=83.0,
                economy=75.0,
            ),
            session(
                4,
                efficiency=76.0,
                contact=135.0,
                cadence=270.0,
                symmetry=82.0,
                economy=74.0,
            ),
        ]

        result = detect_fatigue_signature(
            fatigued
        )

        self.assertTrue(
            result[
                "pattern_detected"
            ]
        )

    def test_trainability(self) -> None:
        result = calculate_trainability_index(
            consistency_score=84.0,
            improvement_potential_score=88.0,
            coach_rule_response_score=82.0,
            session_adherence_score=90.0,
            fatigue_resilience_score=86.0,
            measurement_confidence_score=92.0,
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertGreater(
            result[
                "trainability_index"
            ],
            80.0,
        )

    def test_full_engine(self) -> None:
        result = analyze_athlete_intelligence(
            sessions=self.sessions,
            benchmark_percentiles=(
                self.percentiles
            ),
            coach_rule_response_score=82.0,
            session_adherence_score=90.0,
            measurement_confidence_score=92.0,
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertIn(
            "strength_profile",
            result,
        )

        self.assertIn(
            "weakness_profile",
            result,
        )

        self.assertIn(
            "trainability",
            result,
        )

        self.assertIsNotNone(
            result[
                "overall_athlete_intelligence_score"
            ]
        )


if __name__ == "__main__":
    unittest.main()
