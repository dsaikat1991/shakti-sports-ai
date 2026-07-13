from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.leg_spring_models import (
    LegSpringFrame,
    LegSpringMetrics,
)
from app.services.sprint.leg_spring_scoring import (
    coefficient_of_variation_percent,
    confidence_percent,
    inverse_score,
    rating_for_score,
    target_score,
    weighted_score,
)


SUPPORTED_PHASES = {
    "drive",
    "transition",
    "maximum_velocity",
}


def _ordered_contact_frames(
    frames: list[LegSpringFrame],
    *,
    side: str,
    phase: str,
) -> list[LegSpringFrame]:
    return sorted(
        [
            frame
            for frame in frames
            if frame.side == side
            and frame.phase == phase
            and frame.contact_probability >= 0.50
        ],
        key=lambda frame: (
            frame.timestamp_ms,
            frame.frame_index,
        ),
    )


def _body_height_proxy(
    frame: LegSpringFrame,
) -> float:
    values = [
        frame.hip_y,
        frame.knee_y,
        frame.ankle_y,
        frame.foot_y,
        frame.com_y,
    ]

    return max(
        max(values) - min(values),
        1e-6,
    )


def _compression_series(
    frames: list[LegSpringFrame],
) -> list[float]:
    if not frames:
        return []

    initial_com = frames[0].com_y

    return [
        max(
            0.0,
            frame.com_y - initial_com,
        )
        / _body_height_proxy(frame)
        for frame in frames
    ]


def _elastic_return_ratio(
    compression: list[float],
) -> float | None:
    if len(compression) < 3:
        return None

    peak = max(compression)

    if peak <= 1e-12:
        return 0.0

    final = compression[-1]

    recovered = max(
        0.0,
        peak - final,
    )

    return round(
        min(
            1.0,
            recovered / peak,
        )
        * 100.0,
        2,
    )


def _recovery_timing_percent(
    compression: list[float],
) -> float | None:
    if len(compression) < 3:
        return None

    peak_index = max(
        range(len(compression)),
        key=compression.__getitem__,
    )

    remaining = (
        len(compression)
        - 1
        - peak_index
    )

    if remaining <= 0:
        return 100.0

    return round(
        peak_index
        / max(
            len(compression) - 1,
            1,
        )
        * 100.0,
        2,
    )


def _contact_time(
    frames: list[LegSpringFrame],
) -> float | None:
    explicit = [
        frame.ground_contact_ms
        for frame in frames
        if frame.ground_contact_ms
        is not None
    ]

    if explicit:
        return float(
            mean(explicit)
        )

    if len(frames) < 2:
        return None

    return float(
        frames[-1].timestamp_ms
        - frames[0].timestamp_ms
    )


def analyze_leg_spring(
    frames: list[LegSpringFrame],
    *,
    side: str,
    phase: str,
) -> dict[str, Any]:
    if phase not in SUPPORTED_PHASES:
        return {
            "status": "unsupported_phase",
            "metrics": None,
        }

    selected = _ordered_contact_frames(
        frames,
        side=side,
        phase=phase,
    )

    if len(selected) < 4:
        return {
            "status": "insufficient_data",
            "metrics": None,
        }

    compression_series = (
        _compression_series(
            selected
        )
    )

    maximum_compression = max(
        compression_series
    )

    elastic_return = (
        _elastic_return_ratio(
            compression_series
        )
    )

    recovery_timing = (
        _recovery_timing_percent(
            compression_series
        )
    )

    contact_time_ms = _contact_time(
        selected
    )

    contact_compression_rate = (
        maximum_compression
        / (
            contact_time_ms / 1000.0
        )
        if contact_time_ms is not None
        and contact_time_ms > 1e-9
        else None
    )

    stiffness_index = (
        100.0
        * (
            1.0
            - min(
                1.0,
                maximum_compression / 0.22,
            )
        )
        * (
            1.0
            - min(
                1.0,
                max(
                    0.0,
                    (
                        contact_time_ms
                        - 90.0
                    )
                    / 180.0,
                ),
            )
        )
        if contact_time_ms is not None
        else None
    )

    reactive_compression_score = target_score(
        maximum_compression,
        ideal_min=0.04,
        ideal_max=0.14,
        tolerance=0.16,
    )

    return_score = target_score(
        elastic_return,
        ideal_min=75.0,
        ideal_max=100.0,
        tolerance=45.0,
    )

    timing_score = target_score(
        recovery_timing,
        ideal_min=35.0,
        ideal_max=65.0,
        tolerance=40.0,
    )

    bounce_efficiency = weighted_score(
        [
            (
                reactive_compression_score,
                0.35,
            ),
            (
                return_score,
                0.40,
            ),
            (
                timing_score,
                0.25,
            ),
        ]
    )

    compression_cv = (
        coefficient_of_variation_percent(
            compression_series
        )
    )

    spring_stability = inverse_score(
        compression_cv,
        ideal_max=12.0,
        poor_max=55.0,
    )

    overall = weighted_score(
        [
            (
                stiffness_index,
                0.30,
            ),
            (
                reactive_compression_score,
                0.15,
            ),
            (
                return_score,
                0.20,
            ),
            (
                timing_score,
                0.10,
            ),
            (
                bounce_efficiency,
                0.15,
            ),
            (
                spring_stability,
                0.10,
            ),
        ]
    )

    confidence = confidence_percent(
        [
            frame.confidence
            for frame in selected
        ]
    )

    metrics = LegSpringMetrics(
        side=side,
        phase=phase,
        frames_used=len(selected),
        estimated_leg_compression_normalized=round(
            maximum_compression,
            6,
        ),
        elastic_return_ratio=(
            elastic_return
        ),
        dynamic_leg_stiffness_index=(
            round(
                stiffness_index,
                2,
            )
            if stiffness_index
            is not None
            else None
        ),
        reactive_compression_score=(
            reactive_compression_score
        ),
        elastic_recovery_timing_percent=(
            recovery_timing
        ),
        contact_compression_rate=(
            round(
                contact_compression_rate,
                6,
            )
            if contact_compression_rate
            is not None
            else None
        ),
        vertical_bounce_efficiency_score=(
            bounce_efficiency
        ),
        spring_stability_score=(
            spring_stability
        ),
        overall_leg_spring_score=(
            overall
        ),
        rating=rating_for_score(
            overall
        ),
        confidence=confidence,
    )

    evidence: list[str] = []
    warnings: list[str] = []

    if elastic_return is not None:
        if elastic_return >= 80.0:
            evidence.append(
                "COM recovery after peak compression is efficient."
            )
        elif elastic_return < 55.0:
            warnings.append(
                "Elastic return after peak compression is limited."
            )

    if reactive_compression_score is not None:
        if reactive_compression_score >= 85.0:
            evidence.append(
                "Estimated compression falls within the provisional reactive range."
            )
        elif reactive_compression_score < 60.0:
            warnings.append(
                "Estimated compression is outside the provisional reactive range."
            )

    if spring_stability is not None:
        if spring_stability >= 80.0:
            evidence.append(
                "Compression behaviour is stable through the contact sequence."
            )
        elif spring_stability < 55.0:
            warnings.append(
                "Compression behaviour is inconsistent."
            )

    if (
        stiffness_index is not None
        and stiffness_index < 55.0
    ):
        warnings.append(
            "The dynamic stiffness proxy is low for the analysed phase."
        )

    return {
        "status": "experimental",
        "metrics": metrics.to_dict(),
        "evidence": evidence,
        "warnings": warnings,
        "supporting_measurements": {
            "average_contact_time_ms": (
                round(
                    contact_time_ms,
                    2,
                )
                if contact_time_ms
                is not None
                else None
            ),
            "compression_cv_percent": (
                round(
                    compression_cv,
                    2,
                )
                if compression_cv
                is not None
                else None
            ),
        },
        "method": (
            "com_compression_contact_time_recovery_proxy_v0.1"
        ),
        "validation_level": "experimental",
        "engine_version": "0.1.0",
        "limitations": [
            "This is a video-derived spring index, not laboratory leg stiffness.",
            "No values are reported in kN/m or as a physical spring constant.",
            "COM position is estimated from 2D pose and is sensitive to camera perspective.",
            "Contact timing and compression thresholds require validation against instrumented sprint data.",
        ],
    }


def analyze_leg_spring_by_phase(
    frames: list[LegSpringFrame],
) -> dict[str, Any]:
    results: dict[
        str,
        dict[str, Any],
    ] = {}

    scores: list[float] = []

    for side in (
        "left",
        "right",
    ):
        results[side] = {}

        for phase in (
            "drive",
            "transition",
            "maximum_velocity",
        ):
            result = analyze_leg_spring(
                frames,
                side=side,
                phase=phase,
            )

            results[side][phase] = result

            if (
                result["status"]
                == "experimental"
                and result["metrics"][
                    "overall_leg_spring_score"
                ]
                is not None
            ):
                scores.append(
                    result["metrics"][
                        "overall_leg_spring_score"
                    ]
                )

    return {
        "status": (
            "completed"
            if scores
            else "insufficient_data"
        ),
        "sides": results,
        "overall_average_leg_spring_score": (
            round(
                mean(scores),
                2,
            )
            if scores
            else None
        ),
        "engine_version": "0.1.0",
    }
