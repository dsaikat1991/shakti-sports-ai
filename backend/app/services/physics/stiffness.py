from __future__ import annotations

from typing import Any


def estimate_vertical_stiffness_proxy(
    *,
    vertical_velocity_before_contact: float,
    vertical_velocity_after_contact: float,
    vertical_com_displacement: float,
    contact_time_ms: float,
    confidence: float,
) -> dict[str, Any]:
    """
    Estimate a normalized vertical stiffness proxy.

    This is not laboratory-measured stiffness. It uses change in vertical
    velocity divided by COM compression over the contact window.
    """

    if contact_time_ms <= 0:
        return {
            "status": "insufficient_data",
            "normalized_vertical_stiffness": None,
        }

    displacement = abs(
        vertical_com_displacement
    )

    if displacement <= 1e-9:
        return {
            "status": "insufficient_data",
            "normalized_vertical_stiffness": None,
        }

    delta_velocity = abs(
        vertical_velocity_after_contact
        - vertical_velocity_before_contact
    )

    contact_seconds = (
        contact_time_ms / 1000.0
    )

    normalized_force_proxy = (
        delta_velocity / contact_seconds
    )

    stiffness = (
        normalized_force_proxy / displacement
    )

    return {
        "status": "experimental",
        "normalized_vertical_stiffness": round(
            stiffness,
            6,
        ),
        "contact_time_ms": round(
            contact_time_ms,
            2,
        ),
        "com_displacement": round(
            displacement,
            6,
        ),
        "confidence": round(
            max(
                0.0,
                min(
                    1.0,
                    confidence,
                ),
            )
            * 100.0,
            2,
        ),
        "warning": (
            "This is a normalized image-space stiffness proxy, not a "
            "force-plate or musculoskeletal-model measurement."
        ),
    }
