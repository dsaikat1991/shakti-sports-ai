from __future__ import annotations


def build_readiness_flags(
    *,
    personal_best_detected: bool,
    plateau_detected: bool,
    fatigue_pattern_detected: bool,
    technique_regression_detected: bool,
    mechanical_breakthrough_detected: bool,
    measurement_confidence_score: float | None,
) -> tuple[str, ...]:
    flags: list[str] = []

    if personal_best_detected:
        flags.append(
            "personal_best"
        )

    if plateau_detected:
        flags.append(
            "plateau_detected"
        )

    if fatigue_pattern_detected:
        flags.append(
            "possible_fatigue"
        )

    if technique_regression_detected:
        flags.append(
            "technique_regression"
        )

    if mechanical_breakthrough_detected:
        flags.append(
            "mechanical_breakthrough"
        )

    if (
        measurement_confidence_score
        is not None
        and measurement_confidence_score < 70.0
    ):
        flags.append(
            "low_measurement_confidence"
        )

    return tuple(flags)
