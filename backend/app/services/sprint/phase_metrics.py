from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.phase_models import (
    SprintPhaseFrame,
    SprintSignalFrame,
)


def summarize_metrics_by_phase(
    signal_frames: list[SprintSignalFrame],
    phase_frames: list[SprintPhaseFrame],
) -> dict[str, Any]:
    signal_by_time = {
        frame.timestamp_ms: frame
        for frame in signal_frames
    }

    grouped: dict[
        str,
        list[SprintSignalFrame],
    ] = {}

    for phase_frame in phase_frames:
        signal = signal_by_time.get(
            phase_frame.timestamp_ms
        )

        if signal is None:
            continue

        grouped.setdefault(
            phase_frame.phase,
            [],
        ).append(
            signal
        )

    result: dict[str, Any] = {}

    for phase, frames in grouped.items():
        cadence = [
            frame.cadence_spm
            for frame in frames
            if frame.cadence_spm is not None
        ]

        contact = [
            frame.ground_contact_ms
            for frame in frames
            if frame.ground_contact_ms is not None
        ]

        flight = [
            frame.flight_time_ms
            for frame in frames
            if frame.flight_time_ms is not None
        ]

        torso = [
            frame.torso_angle_deg
            for frame in frames
            if frame.torso_angle_deg is not None
        ]

        result[phase] = {
            "frames": len(frames),
            "average_velocity_x": round(
                mean(
                    frame.com_velocity_x
                    for frame in frames
                ),
                6,
            ),
            "average_acceleration_x": round(
                mean(
                    frame.com_acceleration_x
                    for frame in frames
                ),
                6,
            ),
            "average_cadence_spm": (
                round(mean(cadence), 2)
                if cadence
                else None
            ),
            "average_ground_contact_ms": (
                round(mean(contact), 2)
                if contact
                else None
            ),
            "average_flight_time_ms": (
                round(mean(flight), 2)
                if flight
                else None
            ),
            "average_torso_angle_deg": (
                round(mean(torso), 2)
                if torso
                else None
            ),
        }

    return {
        "status": (
            "completed"
            if result
            else "insufficient_data"
        ),
        "phases": result,
    }
