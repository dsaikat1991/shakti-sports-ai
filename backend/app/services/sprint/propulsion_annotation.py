from __future__ import annotations

from typing import Any

from app.services.sprint.propulsion_models import (
    ContactMotionFrame,
)


def build_contact_phase_annotations(
    frames: list[ContactMotionFrame],
) -> list[dict[str, Any]]:
    annotations: list[
        dict[str, Any]
    ] = []

    for frame in frames:
        if frame.contact_probability < 0.50:
            continue

        if frame.com_acceleration_x < 0.0:
            label = "braking"
        elif frame.com_acceleration_x > 0.0:
            label = "propulsion"
        else:
            label = "neutral"

        annotations.append(
            {
                "frame_index": frame.frame_index,
                "timestamp_ms": frame.timestamp_ms,
                "side": frame.side,
                "phase": frame.phase,
                "label": label,
                "confidence": round(
                    max(
                        0.0,
                        min(
                            1.0,
                            frame.confidence,
                        ),
                    )
                    * 100.0,
                    2,
                ),
            }
        )

    return annotations
