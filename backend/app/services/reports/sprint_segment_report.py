from __future__ import annotations

from typing import Any

JOINT_ANGLE_LABELS: dict[str, str] = {
    "left_knee": "Left knee angle",
    "right_knee": "Right knee angle",
    "left_hip": "Left hip angle",
    "right_hip": "Right hip angle",
    "left_elbow": "Left elbow angle",
    "right_elbow": "Right elbow angle",
}


def _joint_angle_summary(
    joint_angle_summary: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}

    for name, label in JOINT_ANGLE_LABELS.items():
        stats = joint_angle_summary.get(name)
        if not stats:
            continue

        summary[name] = {
            "label": label,
            "coverage_percent": stats.get("coverage_percent"),
            "mean_degrees": stats.get("average_degrees"),
            "min_degrees": stats.get("minimum_degrees"),
            "max_degrees": stats.get("maximum_degrees"),
            "range_degrees": stats.get("range_degrees"),
        }

    return summary


def build_sprint_segment_report(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Turn one segment's raw biomechanics analysis (the output of
    ``analyze_sprint_segment`` / ``build_sprint_biomechanics_preview``)
    into a compact report of the headline sprint metrics.

    Every underlying metric here is still an experimental proxy - see
    ``analysis["limitations"]`` - this only reshapes and labels them.
    """
    segment = analysis.get("segment", {})

    if analysis.get("status") != "completed":
        return {
            "status": analysis.get("status", "skipped"),
            "reason": analysis.get("reason"),
            "segment": segment,
        }

    cadence = analysis.get("cadence", {})
    running_cycles = analysis.get("running_cycles", {})
    ground_contact = analysis.get("ground_contact", {})
    overall_contact = ground_contact.get("overall", {})
    flight_time = analysis.get("flight_time", {})
    duty_factor = analysis.get("duty_factor", {})
    knee_symmetry = analysis.get("knee_symmetry", {})

    return {
        "status": "completed",
        "segment": segment,
        "frames_analyzed": analysis.get("frames_analyzed"),
        "cadence": {
            "status": cadence.get("status"),
            "steps_per_minute": cadence.get("estimated_steps_per_minute"),
            "events_used": cadence.get("events_used"),
            "method": cadence.get("method"),
        },
        "stride": {
            "status": running_cycles.get("status"),
            "stride_frequency_hz": running_cycles.get(
                "estimated_stride_frequency_hz"
            ),
            "median_stride_duration_ms": running_cycles.get(
                "median_stride_duration_ms"
            ),
            "cycles_used": running_cycles.get("cycles_used"),
        },
        "ground_contact": {
            "status": ground_contact.get("status"),
            "events": overall_contact.get("events"),
            "median_contact_time_ms": overall_contact.get(
                "median_contact_time_ms"
            ),
        },
        "flight_time": {
            "status": flight_time.get("status"),
            "median_flight_time_ms": flight_time.get("median_flight_time_ms"),
            "events_used": flight_time.get("events_used"),
        },
        "duty_factor_percent": duty_factor.get("duty_factor_percent"),
        "knee_symmetry_score": knee_symmetry.get("symmetry_score"),
        "joint_angles": _joint_angle_summary(
            analysis.get("joint_angle_summary", {})
        ),
        "limitations": analysis.get("limitations", []),
    }


def build_sprint_stream_report(stream_analysis: dict[str, Any]) -> dict[str, Any]:
    """Build a report for every segment in an ``analyze_sprint_stream`` result."""
    return {
        "provider": stream_analysis.get("provider"),
        "fps": stream_analysis.get("fps"),
        "observed_frames": stream_analysis.get("observed_frames"),
        "interpolated_frames": stream_analysis.get("interpolated_frames"),
        "unbridged_gaps": stream_analysis.get("unbridged_gaps"),
        "segments": [
            build_sprint_segment_report(segment)
            for segment in stream_analysis.get("segments", [])
        ],
    }


def _format_angle_lines(stats: dict[str, Any]) -> list[str]:
    lines = [str(stats["label"])]

    if stats.get("mean_degrees") is not None:
        lines.append(f"  mean: {stats['mean_degrees']:.0f} deg")
    if stats.get("max_degrees") is not None:
        lines.append(f"  max: {stats['max_degrees']:.0f} deg")
    if stats.get("min_degrees") is not None:
        lines.append(f"  min: {stats['min_degrees']:.0f} deg")
    if stats.get("coverage_percent") is not None:
        lines.append(f"  coverage: {stats['coverage_percent']:.1f}%")

    return lines


def format_segment_report_text(
    report: dict[str, Any],
    *,
    index: int | None = None,
) -> str:
    """Render one segment report (from ``build_sprint_segment_report``) as text."""
    lines: list[str] = [f"Segment {index}" if index is not None else "Segment"]

    if report.get("status") != "completed":
        lines.append(f"  status: {report.get('status')} ({report.get('reason')})")
        return "\n".join(lines)

    segment = report.get("segment", {})
    lines.append(f"Frames: {segment.get('frame_count')}")

    cadence = report.get("cadence", {})
    if cadence.get("steps_per_minute") is not None:
        lines.append(f"Cadence: {cadence['steps_per_minute']:.1f} steps/min")
    else:
        lines.append(f"Cadence: {cadence.get('status', 'insufficient_data')}")

    stride = report.get("stride", {})
    if stride.get("stride_frequency_hz") is not None:
        lines.append(
            f"Stride frequency: {stride['stride_frequency_hz']:.2f} strides/sec"
        )

    ground_contact = report.get("ground_contact", {})
    if ground_contact.get("events") is not None:
        lines.append(f"Ground contacts: {ground_contact['events']}")

    flight_time = report.get("flight_time", {})
    if flight_time.get("median_flight_time_ms") is not None:
        lines.append(
            f"Flight time: {flight_time['median_flight_time_ms'] / 1000:.3f} s"
        )

    if report.get("duty_factor_percent") is not None:
        lines.append(f"Duty factor: {report['duty_factor_percent']:.1f}%")

    if report.get("knee_symmetry_score") is not None:
        lines.append(f"Knee symmetry: {report['knee_symmetry_score']:.1f}/100")

    for stats in report.get("joint_angles", {}).values():
        lines.append("")
        lines.extend(_format_angle_lines(stats))

    return "\n".join(lines)


def format_stream_report_text(report: dict[str, Any]) -> str:
    """Render a full ``build_sprint_stream_report`` result as text."""
    blocks = [
        format_segment_report_text(segment, index=index)
        for index, segment in enumerate(report.get("segments", []))
    ]

    return "\n\n".join(blocks)
