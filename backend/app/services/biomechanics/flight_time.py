from __future__ import annotations

from statistics import mean, median
from typing import Any


def _flatten_contact_events(
    contact_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> list[dict[str, int | float | str]]:
    events: list[dict[str, int | float | str]] = []

    for side in ("left", "right"):
        for event in contact_events.get(side, []):
            start = event.get("contact_start_ms")
            end = event.get("contact_end_ms")

            if not isinstance(start, int) or not isinstance(end, int):
                continue

            if end <= start:
                continue

            events.append(
                {
                    **event,
                    "side": side,
                }
            )

    return sorted(
        events,
        key=lambda event: int(
            event["contact_start_ms"]
        ),
    )


def estimate_flight_times(
    contact_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> dict[str, Any]:
    """
    Estimate airborne time as the gap between one detected contact ending
    and the next contact beginning.

    This inherits all limitations of the provisional contact detector.
    """

    ordered = _flatten_contact_events(contact_events)

    if len(ordered) < 2:
        return {
            "status": "insufficient_data",
            "events": [],
            "average_flight_time_ms": None,
            "median_flight_time_ms": None,
            "events_used": 0,
            "method": "inter_contact_gap_proxy",
        }

    events: list[dict[str, int | str]] = []

    for previous, current in zip(
        ordered[:-1],
        ordered[1:],
    ):
        previous_end = int(
            previous["contact_end_ms"]
        )
        current_start = int(
            current["contact_start_ms"]
        )

        flight_ms = current_start - previous_end

        # Conservative plausibility range for running/sprinting.
        if not 20 <= flight_ms <= 500:
            continue

        events.append(
            {
                "from_side": str(
                    previous.get("side", "unknown")
                ),
                "to_side": str(
                    current.get("side", "unknown")
                ),
                "start_ms": previous_end,
                "end_ms": current_start,
                "flight_time_ms": flight_ms,
            }
        )

    if not events:
        return {
            "status": "low_confidence",
            "events": [],
            "average_flight_time_ms": None,
            "median_flight_time_ms": None,
            "events_used": 0,
            "method": "inter_contact_gap_proxy",
        }

    values = [
        float(event["flight_time_ms"])
        for event in events
    ]

    return {
        "status": "experimental",
        "events": events,
        "average_flight_time_ms": round(
            mean(values),
            2,
        ),
        "median_flight_time_ms": round(
            median(values),
            2,
        ),
        "events_used": len(events),
        "method": "inter_contact_gap_proxy",
        "warning": (
            "Flight time is derived from experimental image-space "
            "contact events and is not force-plate validated."
        ),
    }


def estimate_duty_factor(
    ground_contact: dict[str, Any],
    flight_time: dict[str, Any],
) -> dict[str, Any]:
    """
    Estimate duty factor as contact / (contact + flight).

    A value is returned only when both contact and flight summaries exist.
    """

    contact_ms = (
        ground_contact.get("overall", {})
        .get("median_contact_time_ms")
    )

    flight_ms = flight_time.get(
        "median_flight_time_ms"
    )

    if not isinstance(contact_ms, (int, float)):
        return {
            "status": "insufficient_data",
            "duty_factor_percent": None,
        }

    if not isinstance(flight_ms, (int, float)):
        return {
            "status": "insufficient_data",
            "duty_factor_percent": None,
        }

    cycle_ms = float(contact_ms) + float(flight_ms)

    if cycle_ms <= 0:
        return {
            "status": "insufficient_data",
            "duty_factor_percent": None,
        }

    return {
        "status": "experimental",
        "duty_factor_percent": round(
            float(contact_ms) / cycle_ms * 100.0,
            2,
        ),
        "median_contact_time_ms": round(
            float(contact_ms),
            2,
        ),
        "median_flight_time_ms": round(
            float(flight_ms),
            2,
        ),
        "warning": (
            "Duty factor inherits uncertainty from experimental "
            "contact and flight-time estimates."
        ),
    }
