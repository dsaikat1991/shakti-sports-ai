import unittest

from app.services.biomechanics.motion_reconstruction import (
    LandmarkObservation,
    reconstruct_trajectory,
)


class TestMotionReconstruction(unittest.TestCase):
    def test_predicts_through_short_gap(self) -> None:
        observations = [
            LandmarkObservation(
                frame_index=0,
                timestamp_ms=0,
                x=0.0,
                y=0.0,
                confidence=1.0,
            ),
            LandmarkObservation(
                frame_index=1,
                timestamp_ms=50,
                x=0.1,
                y=0.0,
                confidence=1.0,
            ),
            LandmarkObservation(
                frame_index=2,
                timestamp_ms=100,
                x=None,
                y=None,
                confidence=0.0,
            ),
            LandmarkObservation(
                frame_index=3,
                timestamp_ms=150,
                x=0.3,
                y=0.0,
                confidence=1.0,
            ),
        ]

        result = reconstruct_trajectory(
            observations,
            maximum_prediction_gap_ms=120,
        )

        predicted = [
            point
            for point in result
            if point.source == "predicted"
        ]

        self.assertEqual(
            len(predicted),
            1,
        )

    def test_drops_long_gap(self) -> None:
        observations = [
            LandmarkObservation(
                frame_index=0,
                timestamp_ms=0,
                x=0.0,
                y=0.0,
                confidence=1.0,
            ),
            LandmarkObservation(
                frame_index=1,
                timestamp_ms=300,
                x=None,
                y=None,
                confidence=0.0,
            ),
        ]

        result = reconstruct_trajectory(
            observations,
            maximum_prediction_gap_ms=100,
        )

        self.assertEqual(
            len(result),
            1,
        )


if __name__ == "__main__":
    unittest.main()
