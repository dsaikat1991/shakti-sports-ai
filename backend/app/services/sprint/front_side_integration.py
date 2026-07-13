from __future__ import annotations

from typing import Any

from app.services.sprint.front_side_mechanics import (
    analyze_front_side_mechanics,
)
from app.services.sprint.front_side_models import (
    FrontSideFrame,
)


def analyze_front_side_by_phase(
    frames: list[FrontSideFrame],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for side in (
        "left",
        "right",
    ):
        side_result: dict[
            str,
            Any,
        ] = {}

        for phase in (
            "drive",
            "transition",
            "maximum_velocity",
        ):
            side_result[
                phase
            ] = analyze_front_side_mechanics(
                frames,
                side=side,
                phase=phase,
            )

        result[
            side
        ] = side_result

    return {
        "status": "completed",
        "sides": result,
        "engine_version": "0.1.0",
    }
