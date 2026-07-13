import unittest

from app.services.biomechanics.motion_filter import (
    Kalman1D,
)


class TestMotionFilter(unittest.TestCase):
    def test_filter_tracks_linear_motion(self) -> None:
        filter_1d = Kalman1D(
            process_variance=1e-4,
            measurement_variance=1e-3,
        )

        values = [
            filter_1d.update(
                measurement,
                0.1,
                measurement_confidence=1.0,
            )[0]
            for measurement in (
                0.0,
                0.1,
                0.2,
                0.3,
                0.4,
            )
        ]

        self.assertGreater(
            values[-1],
            values[0],
        )

    def test_low_confidence_measurement_has_less_effect(self) -> None:
        high = Kalman1D()
        low = Kalman1D()

        high.update(0.0, 0.1)
        low.update(0.0, 0.1)

        high_position, _ = high.update(
            1.0,
            0.1,
            measurement_confidence=1.0,
        )

        low_position, _ = low.update(
            1.0,
            0.1,
            measurement_confidence=0.1,
        )

        self.assertGreater(
            high_position,
            low_position,
        )


if __name__ == "__main__":
    unittest.main()
