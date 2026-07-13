import unittest

from app.services.biomechanics.confidence_engine import (
    metric_confidence,
    trajectory_continuity_score,
)


class TestConfidenceEngine(unittest.TestCase):
    def test_metric_confidence(self) -> None:
        result = metric_confidence(
            landmark_confidence=0.95,
            trajectory_continuity=0.90,
            camera_confidence=0.98,
            event_confidence=0.92,
        )

        self.assertIsNotNone(
            result["score"],
        )

        self.assertIn(
            result["rating"],
            ("high", "very_high"),
        )

    def test_continuity_score_penalises_missing_points(self) -> None:
        score = trajectory_continuity_score(
            measured_points=8,
            predicted_points=1,
            missing_points=1,
        )

        self.assertLess(
            score,
            1.0,
        )

        self.assertGreater(
            score,
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
