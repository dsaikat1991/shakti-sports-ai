from __future__ import annotations

from typing import Any

from app.services.biomechanics.cadence import (
    estimate_cadence_from_knee_events,
)
from app.services.biomechanics.centre_of_mass import (
    analyze_centre_of_mass,
)
from app.services.biomechanics.contact_events import (
    detect_contact_events,
    summarize_contact_times,
)
from app.services.biomechanics.flight_time import (
    estimate_duty_factor,
    estimate_flight_times,
)
from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_phase import (
    calculate_knee_symmetry,
    detect_knee_cycle_events,
)
from app.services.biomechanics.running_cycle import (
    classify_cycle_phases,
    detect_running_cycles,
)
from app.services.biomechanics.signal_processing import (
    prepare_angle_series,
    robust_angle_summary,
)


ANGLE_NAMES = (
    "left_knee",
    "right_knee",
    "left_hip",
    "right_hip",
    "left_elbow",
    "right_elbow",
)


def summarize_joint_angles(
    frame_metrics: list[FrameMetrics],
) -> dict[str, dict[str, Any]]:
    total_frames = len(frame_metrics)
    summaries: dict[str, dict[str, Any]] = {}

    if total_frames == 0:
        return summaries

    for angle_name in ANGLE_NAMES:
        prepared_series = prepare_angle_series(
            frame_metrics,
            angle_name,
        )

        summary = robust_angle_summary(
            prepared_series
        )

        frames_with_value = int(
            summary["frames_with_value"]
        )

        summary["coverage_percent"] = round(
            frames_with_value / total_frames * 100,
            2,
        )

        summaries[angle_name] = summary

    return summaries


def build_sprint_biomechanics_preview(
    frame_metrics: list[FrameMetrics],
    *,
    analysis_ready: bool,
    readiness_reason: str,
) -> dict[str, Any]:
    empty_events = {
        "left": [],
        "right": [],
    }

    if not analysis_ready:
        return {
            "status": "skipped",
            "reason": readiness_reason,
            "frames_analyzed": 0,
            "joint_angle_summary": {},
            "knee_cycle_events": empty_events,
            "knee_symmetry": {
                "status": "not_analyzed",
            },
            "cadence": {
                "status": "not_analyzed",
            },
            "contact_events": empty_events,
            "ground_contact": {
                "status": "not_analyzed",
            },
            "flight_time": {
                "status": "not_analyzed",
            },
            "duty_factor": {
                "status": "not_analyzed",
            },
            "running_cycles": {
                "status": "not_analyzed",
            },
            "phase_timeline": {
                "status": "not_analyzed",
            },
            "centre_of_mass": {
                "status": "not_analyzed",
            },
        }

    knee_cycle_events = detect_knee_cycle_events(
        frame_metrics
    )

    contact_events = detect_contact_events(
        frame_metrics
    )

    ground_contact = summarize_contact_times(
        contact_events
    )

    flight_time = estimate_flight_times(
        contact_events
    )

    return {
        "status": "completed",
        "reason": None,
        "frames_analyzed": len(frame_metrics),
        "joint_angle_summary": summarize_joint_angles(
            frame_metrics
        ),
        "knee_cycle_events": knee_cycle_events,
        "knee_symmetry": calculate_knee_symmetry(
            frame_metrics
        ),
        "cadence": estimate_cadence_from_knee_events(
            knee_cycle_events
        ),
        "contact_events": contact_events,
        "ground_contact": ground_contact,
        "flight_time": flight_time,
        "duty_factor": estimate_duty_factor(
            ground_contact,
            flight_time,
        ),
        "running_cycles": detect_running_cycles(
            contact_events
        ),
        "phase_timeline": classify_cycle_phases(
            contact_events,
            flight_time,
        ),
        "centre_of_mass": analyze_centre_of_mass(
            frame_metrics
        ),
        "signal_processing": {
            "multi_segment_extrema_detection": True,
            "local_hampel_outlier_filtering": True,
            "moving_average_window": 5,
            "summary_percentiles": [5, 95],
        },
        "limitations": [
            "Angles remain projected 2D image-plane measurements.",
            "Cadence (from knee-flexion timing) has been ground-truth "
            "checked against real footage and is directionally reliable, "
            "but remains an experimental proxy, not force-plate validated.",
            "Ground contact, flight time, and duty factor have a CONFIRMED "
            "issue for low/close camera angles: the detector can fire on "
            "swing-phase peak flexion instead of true ground contact. Do "
            "not treat contact_time_ms/flight_time/duty_factor as "
            "reliable until this is fixed - see contact_events.py.",
            "The centre-of-mass result is a weighted landmark-centre proxy.",
            "Vertical oscillation is reported relative to normalized body height.",
            "These outputs are not laboratory or force-plate validated.",
        ],
    }
