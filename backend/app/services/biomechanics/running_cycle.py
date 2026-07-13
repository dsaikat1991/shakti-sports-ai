from __future__ import annotations

from statistics import mean, median
from typing import Any


def _ordered_contacts(
    contact_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> list[dict[str, int | float | str]]:
    contacts: list[dict[str, int | float | str]] = []

    for side in ("left", "right"):
        for event in contact_events.get(side, []):
            start = event.get("contact_start_ms")

            if not isinstance(start, int):
                continue

            contacts.append(
                {
                    **event,
                    "side": side,
                }
            )

    return sorted(
        contacts,
        key=lambda event: int(
            event["contact_start_ms"]
        ),
    )


def detect_running_cycles(
    contact_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> dict[str, Any]:
    """
    Detect provisional stride cycles from same-side contact starts.

    One stride cycle runs from a left contact to the next left contact,
    or from a right contact to the next right contact.
    """

    ordered = _ordered_contacts(contact_events)

    by_side = {
        "left": [
            event
            for event in ordered
            if event.get("side") == "left"
        ],
        "right": [
            event
            for event in ordered
            if event.get("side") == "right"
        ],
    }

    cycles: list[dict[str, int | str]] = []

    for side in ("left", "right"):
        side_events = by_side[side]

        for previous, current in zip(
            side_events[:-1],
            side_events[1:],
        ):
            start_ms = int(
                previous["contact_start_ms"]
            )
            end_ms = int(
                current["contact_start_ms"]
            )
            duration_ms = end_ms - start_ms

            if not 200 <= duration_ms <= 2000:
                continue

            cycles.append(
                {
                    "side": side,
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "stride_duration_ms": duration_ms,
                }
            )

    cycles.sort(
        key=lambda cycle: int(
            cycle["start_ms"]
        )
    )

    if not cycles:
        return {
            "status": "insufficient_data",
            "cycles": [],
            "average_stride_duration_ms": None,
            "median_stride_duration_ms": None,
            "estimated_stride_frequency_hz": None,
            "cycles_used": 0,
            "method": "same_side_contact_interval_proxy",
        }

    durations = [
        float(cycle["stride_duration_ms"])
        for cycle in cycles
    ]

    median_duration = float(
        median(durations)
    )

    frequency_hz = (
        1000.0 / median_duration
        if median_duration > 0
        else None
    )

    return {
        "status": "experimental",
        "cycles": cycles,
        "average_stride_duration_ms": round(
            mean(durations),
            2,
        ),
        "median_stride_duration_ms": round(
            median_duration,
            2,
        ),
        "estimated_stride_frequency_hz": (
            round(frequency_hz, 3)
            if frequency_hz is not None
            else None
        ),
        "cycles_used": len(cycles),
        "method": "same_side_contact_interval_proxy",
        "warning": (
            "Running cycles are inferred from experimental contact "
            "events and are not independently validated."
        ),
    }


def classify_cycle_phases(
    contact_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
    flight_time: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a simple event-based phase timeline.

    Phases are limited to contact and flight because toe-off, swing,
    pre-contact and push-off are not yet independently detected.
    """

    timeline: list[dict[str, int | str]] = []

    for side in ("left", "right"):
        for event in contact_events.get(side, []):
            start = event.get("contact_start_ms")
            end = event.get("contact_end_ms")

            if not isinstance(start, int) or not isinstance(end, int):
                continue

            timeline.append(
                {
                    "phase": "contact",
                    "side": side,
                    "start_ms": start,
                    "end_ms": end,
                    "duration_ms": end - start,
                }
            )

    for event in flight_time.get("events", []):
        start = event.get("start_ms")
        end = event.get("end_ms")

        if not isinstance(start, int) or not isinstance(end, int):
            continue

        timeline.append(
            {
                "phase": "flight",
                "side": "none",
                "start_ms": start,
                "end_ms": end,
                "duration_ms": end - start,
            }
        )

    timeline.sort(
        key=lambda item: int(
            item["start_ms"]
        )
    )

    return {
        "status": (
            "experimental"
            if timeline
            else "insufficient_data"
        ),
        "timeline": timeline,
        "phases_supported": [
            "contact",
            "flight",
        ],
        "phases_not_yet_supported": [
            "toe_off",
            "early_swing",
            "mid_swing",
            "late_swing",
            "pre_contact",
            "push_off",
        ],
    }
