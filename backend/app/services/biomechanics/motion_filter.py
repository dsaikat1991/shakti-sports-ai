from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Kalman1D:
    process_variance: float = 1e-4
    measurement_variance: float = 1e-2

    position: float | None = None
    velocity: float = 0.0

    position_variance: float = 1.0
    velocity_variance: float = 1.0
    covariance: float = 0.0

    def reset(self) -> None:
        self.position = None
        self.velocity = 0.0
        self.position_variance = 1.0
        self.velocity_variance = 1.0
        self.covariance = 0.0

    def predict(
        self,
        dt_seconds: float,
    ) -> tuple[float | None, float]:
        if self.position is None:
            return None, self.velocity

        self.position = (
            self.position
            + self.velocity * dt_seconds
        )

        predicted_position_variance = (
            self.position_variance
            + 2.0 * dt_seconds * self.covariance
            + (dt_seconds**2) * self.velocity_variance
            + self.process_variance
        )

        predicted_covariance = (
            self.covariance
            + dt_seconds * self.velocity_variance
        )

        predicted_velocity_variance = (
            self.velocity_variance
            + self.process_variance
        )

        self.position_variance = (
            predicted_position_variance
        )
        self.covariance = (
            predicted_covariance
        )
        self.velocity_variance = (
            predicted_velocity_variance
        )

        return self.position, self.velocity

    def update(
        self,
        measurement: float,
        dt_seconds: float,
        *,
        measurement_confidence: float = 1.0,
    ) -> tuple[float, float]:
        confidence = max(
            0.05,
            min(1.0, measurement_confidence),
        )

        adaptive_measurement_variance = (
            self.measurement_variance
            / confidence
        )

        if self.position is None:
            self.position = float(measurement)
            self.velocity = 0.0
            self.position_variance = (
                adaptive_measurement_variance
            )
            return self.position, self.velocity

        self.predict(dt_seconds)

        innovation = (
            measurement - self.position
        )

        innovation_variance = (
            self.position_variance
            + adaptive_measurement_variance
        )

        if innovation_variance <= 0:
            return self.position, self.velocity

        position_gain = (
            self.position_variance
            / innovation_variance
        )

        velocity_gain = (
            self.covariance
            / innovation_variance
        )

        self.position = (
            self.position
            + position_gain * innovation
        )

        self.velocity = (
            self.velocity
            + velocity_gain * innovation
        )

        self.position_variance = (
            (1.0 - position_gain)
            * self.position_variance
        )

        self.velocity_variance = (
            self.velocity_variance
            - velocity_gain * self.covariance
        )

        self.covariance = (
            (1.0 - position_gain)
            * self.covariance
        )

        return self.position, self.velocity


@dataclass(slots=True)
class Kalman2D:
    process_variance: float = 1e-4
    measurement_variance: float = 1e-2

    x_filter: Kalman1D = field(init=False)
    y_filter: Kalman1D = field(init=False)

    def __post_init__(self) -> None:
        self.x_filter = Kalman1D(
            process_variance=self.process_variance,
            measurement_variance=self.measurement_variance,
        )
        self.y_filter = Kalman1D(
            process_variance=self.process_variance,
            measurement_variance=self.measurement_variance,
        )

    def reset(self) -> None:
        self.x_filter.reset()
        self.y_filter.reset()

    def update(
        self,
        x: float,
        y: float,
        dt_seconds: float,
        *,
        measurement_confidence: float = 1.0,
    ) -> tuple[float, float, float, float]:
        filtered_x, velocity_x = (
            self.x_filter.update(
                x,
                dt_seconds,
                measurement_confidence=(
                    measurement_confidence
                ),
            )
        )

        filtered_y, velocity_y = (
            self.y_filter.update(
                y,
                dt_seconds,
                measurement_confidence=(
                    measurement_confidence
                ),
            )
        )

        return (
            filtered_x,
            filtered_y,
            velocity_x,
            velocity_y,
        )
