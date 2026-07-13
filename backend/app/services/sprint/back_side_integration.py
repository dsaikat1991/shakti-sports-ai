from __future__ import annotations

from typing import Any

from app.services.sprint.back_side_mechanics import (
    analyze_back_side_mechanics,
)
from app.services.sprint.back_side_models import (
    BackSideFrame,
)


def analyze_back_side_by_phase(
    frames: list[BackSideFrame],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for side in (
        "left",
        "right",
    ):
        result[side] = {}

        for phase in (
            "drive",
            "transition",
            "maximum_velocity",
        ):
            result[side][phase] = (
                analyze_back_side_mechanics(
                    frames,
                    side=side,
                    phase=phase,
                )
            )

    return {
        "status": "completed",
        "sides": result,
        "engine_version": "0.1.0",
    }
