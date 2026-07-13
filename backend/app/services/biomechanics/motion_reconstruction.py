from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.services.biomechanics.motion_filter import (
    Kalman2D,
)


@dataclass(slots=True, frozen=True)
class LandmarkObservation:
    frame_index: int
    timestamp_ms: int
    x: float | None
    y: float | None
    confidence: float


@dataclass(slots=True, frozen=True)
class ReconstructedPoint:
    frame_index: int
    timestamp_ms: int
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    speed: float
    source: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def reconstruct_trajectory(
    observations: list[LandmarkObservation],
    *,
    maximum_prediction_gap_ms: int = 150,
    process_variance: float = 1e-4,
    measurement_variance: float = 1e-2,
) -> list[ReconstructedPoint]:
    if not observations:
        return []

    ordered = sorted(
        observations,
        key=lambda item: item.timestamp_ms,
    )

    kalman = Kalman2D(
        process_variance=process_variance,
        measurement_variance=measurement_variance,
    )

    result: list[ReconstructedPoint] = []

    previous_timestamp_ms: int | None = None
    last_measurement_timestamp_ms: int | None = None

    for observation in ordered:
        dt_seconds = (
            (
                observation.timestamp_ms
                - previous_timestamp_ms
            )
            / 1000.0
            if previous_timestamp_ms is not None
            else 0.0
        )

        has_measurement = (
            observation.x is not None
            and observation.y is not None
            and observation.confidence > 0.0
        )

        if has_measurement:
            x, y, velocity_x, velocity_y = (
                kalman.update(
                    float(observation.x),
                    float(observation.y),
                    dt_seconds,
                    measurement_confidence=(
                        observation.confidence
                    ),
                )
            )

            source = "measured"
            confidence = observation.confidence
            last_measurement_timestamp_ms = (
                observation.timestamp_ms
            )

        else:
            if (
                last_measurement_timestamp_ms is None
                or observation.timestamp_ms
                - last_measurement_timestamp_ms
                > maximum_prediction_gap_ms
            ):
                kalman.reset()
                previous_timestamp_ms = (
                    observation.timestamp_ms
                )
                continue

            kalman.x_filter.predict(dt_seconds)
            kalman.y_filter.predict(dt_seconds)

            if (
                kalman.x_filter.position is None
                or kalman.y_filter.position is None
            ):
                previous_timestamp_ms = (
                    observation.timestamp_ms
                )
                continue

            x = float(kalman.x_filter.position)
            y = float(kalman.y_filter.position)
            velocity_x = float(
                kalman.x_filter.velocity
            )
            velocity_y = float(
                kalman.y_filter.velocity
            )

            source = "predicted"

            gap_ms = (
                observation.timestamp_ms
                - last_measurement_timestamp_ms
            )

            confidence = max(
                0.0,
                1.0
                - gap_ms
                / maximum_prediction_gap_ms,
            )

        speed = (
            velocity_x**2
            + velocity_y**2
        ) ** 0.5

        result.append(
            ReconstructedPoint(
                frame_index=(
                    observation.frame_index
                ),
                timestamp_ms=(
                    observation.timestamp_ms
                ),
                x=round(x, 6),
                y=round(y, 6),
                velocity_x=round(
                    velocity_x,
                    6,
                ),
                velocity_y=round(
                    velocity_y,
                    6,
                ),
                speed=round(speed, 6),
                source=source,
                confidence=round(
                    confidence,
                    4,
                ),
            )
        )

        previous_timestamp_ms = (
            observation.timestamp_ms
        )

    return result
