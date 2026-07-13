from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.physics.models import (
    EnergyState,
    PowerState,
)


def summarize_mechanical_efficiency(
    energy_states: list[EnergyState],
    power_states: list[PowerState],
) -> dict[str, Any]:
    if not energy_states or not power_states:
        return {
            "status": "insufficient_data",
        }

    positive_power = [
        max(
            0.0,
            state.normalized_total_power,
        )
        for state in power_states
    ]

    horizontal_power = [
        max(
            0.0,
            state.normalized_horizontal_power,
        )
        for state in power_states
    ]

    total_positive = sum(
        positive_power
    )

    horizontal_positive = sum(
        horizontal_power
    )

    directional_efficiency = (
        horizontal_positive / total_positive
        if total_positive > 0.0
        else 0.0
    )

    mechanical_values = [
        state.normalized_mechanical_energy
        for state in energy_states
    ]

    if len(mechanical_values) >= 2:
        energy_variability = (
            max(mechanical_values)
            - min(mechanical_values)
        )
    else:
        energy_variability = 0.0

    confidence = mean(
        state.confidence
        for state in energy_states
    )

    return {
        "status": "experimental",
        "horizontal_power_share_percent": round(
            directional_efficiency
            * 100.0,
            2,
        ),
        "mechanical_energy_range": round(
            energy_variability,
            6,
        ),
        "confidence": round(
            confidence * 100.0,
            2,
        ),
        "warning": (
            "Efficiency values are normalized motion proxies and require "
            "scene calibration and validation before performance claims."
        ),
    }
