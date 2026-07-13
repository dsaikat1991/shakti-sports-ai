from __future__ import annotations

from app.services.physics.models import (
    PhysicsSample,
    PowerState,
)


def compute_normalized_power(
    samples: list[PhysicsSample],
) -> list[PowerState]:
    """
    Compute mass-normalized instantaneous power proxy.

    Power per unit mass is approximated as acceleration dot velocity.
    These values are normalized and camera-relative unless scene scale
    and body mass are available.
    """

    states: list[PowerState] = []

    for sample in samples:
        horizontal = (
            sample.acceleration_x
            * sample.velocity_x
        )

        vertical = (
            sample.acceleration_y
            * sample.velocity_y
        )

        total = horizontal + vertical

        states.append(
            PowerState(
                frame_index=sample.frame_index,
                timestamp_ms=sample.timestamp_ms,
                normalized_horizontal_power=round(
                    horizontal,
                    6,
                ),
                normalized_vertical_power=round(
                    vertical,
                    6,
                ),
                normalized_total_power=round(
                    total,
                    6,
                ),
                confidence=round(
                    max(
                        0.0,
                        min(
                            1.0,
                            sample.confidence,
                        ),
                    ),
                    4,
                ),
            )
        )

    return states
