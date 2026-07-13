from __future__ import annotations

from app.services.physics.models import (
    EnergyState,
    PhysicsSample,
)


GRAVITY = 9.80665


def compute_normalized_energy(
    samples: list[PhysicsSample],
    *,
    gravity: float = GRAVITY,
    reference_height: float | None = None,
) -> list[EnergyState]:
    """
    Compute mass-normalized mechanical energy.

    Kinetic energy is reported as 0.5 * v^2.
    Potential energy is reported as g * h.

    Because monocular video does not provide true scale by default, these
    values are normalized proxies unless scene calibration is available.
    """

    if not samples:
        return []

    if reference_height is None:
        reference_height = min(
            sample.com_y
            for sample in samples
        )

    states: list[EnergyState] = []

    for sample in samples:
        speed_squared = (
            sample.velocity_x**2
            + sample.velocity_y**2
        )

        kinetic = 0.5 * speed_squared

        # Image y increases downward. Use inverted displacement from the
        # chosen reference so greater visual height yields more potential.
        relative_height = (
            reference_height - sample.com_y
        )

        potential = gravity * relative_height
        mechanical = kinetic + potential

        states.append(
            EnergyState(
                frame_index=sample.frame_index,
                timestamp_ms=sample.timestamp_ms,
                normalized_kinetic_energy=round(
                    kinetic,
                    6,
                ),
                normalized_potential_energy=round(
                    potential,
                    6,
                ),
                normalized_mechanical_energy=round(
                    mechanical,
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
