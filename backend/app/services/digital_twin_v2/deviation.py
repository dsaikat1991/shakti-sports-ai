from __future__ import annotations

from typing import Any

from app.services.digital_twin_v2.models import (
    DeviationResult,
    TwinSession,
)


def classify_deviation(
    z_score: float | None,
) -> str:
    if z_score is None:
        return "unavailable"

    absolute = abs(
        z_score
    )

    if absolute < 1.0:
        return "within_normal_range"
    if absolute < 2.0:
        return "moderate_deviation"

    return "significant_deviation"


def compare_current_to_baseline(
    *,
    latest: TwinSession,
    baselines: dict[str, Any],
) -> dict[str, Any]:
    results: dict[str, Any] = {}

    feature_baselines = baselines.get(
        "features",
        {},
    )

    for feature_name, current_value in latest.features.items():
        baseline = feature_baselines.get(
            feature_name
        )

        if not baseline:
            continue

        baseline_mean = float(
            baseline["mean"]
        )

        standard_deviation = float(
            baseline[
                "standard_deviation"
            ]
        )

        z_score = (
            None
            if standard_deviation
            <= 1e-12
            else (
                float(current_value)
                - baseline_mean
            )
            / standard_deviation
        )

        deviation_percent = (
            None
            if abs(baseline_mean)
            <= 1e-12
            else (
                float(current_value)
                - baseline_mean
            )
            / abs(
                baseline_mean
            )
            * 100.0
        )

        confidence = (
            latest.confidences.get(
                feature_name
            )
            * 100.0
            if latest.confidences
            and feature_name
            in latest.confidences
            else None
        )

        result = DeviationResult(
            feature_name=feature_name,
            current_value=float(
                current_value
            ),
            baseline_mean=baseline_mean,
            z_score=(
                round(
                    z_score,
                    4,
                )
                if z_score
                is not None
                else None
            ),
            deviation_percent=(
                round(
                    deviation_percent,
                    2,
                )
                if deviation_percent
                is not None
                else None
            ),
            classification=(
                classify_deviation(
                    z_score
                )
            ),
            confidence=(
                round(
                    confidence,
                    2,
                )
                if confidence
                is not None
                else None
            ),
        )

        results[
            feature_name
        ] = result.to_dict()

    return {
        "status": (
            "completed"
            if results
            else "insufficient_data"
        ),
        "deviations": results,
        "engine_version": "1.0.0",
    }
