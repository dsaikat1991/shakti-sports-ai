from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.physics.efficiency import (
    summarize_mechanical_efficiency,
)
from app.services.physics.energy import (
    compute_normalized_energy,
)
from app.services.physics.models import (
    PhysicsSample,
)
from app.services.physics.power import (
    compute_normalized_power,
)


def build_physics_summary(
    samples: list[PhysicsSample],
) -> dict[str, Any]:
    if not samples:
        return {
            "status": "insufficient_data",
        }

    energy = compute_normalized_energy(
        samples
    )

    power = compute_normalized_power(
        samples
    )

    peak_horizontal_power = max(
        (
            state.normalized_horizontal_power
            for state in power
        ),
        default=None,
    )

    peak_total_power = max(
        (
            state.normalized_total_power
            for state in power
        ),
        default=None,
    )

    average_confidence = mean(
        sample.confidence
        for sample in samples
    )

    return {
        "status": "experimental",
        "samples_used": len(samples),
        "peak_normalized_horizontal_power": (
            round(
                peak_horizontal_power,
                6,
            )
            if peak_horizontal_power
            is not None
            else None
        ),
        "peak_normalized_total_power": (
            round(
                peak_total_power,
                6,
            )
            if peak_total_power
            is not None
            else None
        ),
        "efficiency": (
            summarize_mechanical_efficiency(
                energy,
                power,
            )
        ),
        "average_confidence": round(
            average_confidence * 100.0,
            2,
        ),
        "limitations": [
            "Outputs are mass-normalized.",
            "Coordinates are camera-relative unless scene calibration exists.",
            "These are inferred motion proxies, not direct force measurements.",
        ],
    }
