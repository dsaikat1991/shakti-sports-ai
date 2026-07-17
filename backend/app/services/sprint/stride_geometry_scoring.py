from __future__ import annotations

from math import atan2, degrees, prod
from statistics import mean, pstdev


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


def safe_mean(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return float(
        mean(values)
    )


def coefficient_of_variation_percent(
    values: list[float],
) -> float | None:
    if len(values) < 2:
        return None

    average = mean(values)

    if abs(average) <= 1e-12:
        return None

    return float(
        pstdev(values)
        / abs(average)
        * 100.0
    )


def inverse_cv_score(
    value: float | None,
    *,
    ideal_max: float,
    poor_max: float,
) -> float | None:
    if value is None:
        return None

    if poor_max <= ideal_max:
        raise ValueError(
            "poor_max must be greater than ideal_max."
        )

    if value <= ideal_max:
        return 100.0

    if value >= poor_max:
        return 0.0

    return round(
        (
            1.0
            - (
                value - ideal_max
            )
            / (
                poor_max - ideal_max
            )
        )
        * 100.0,
        2,
    )


def symmetry_score(
    left_value: float | None,
    right_value: float | None,
) -> float | None:
    if (
        left_value is None
        or right_value is None
    ):
        return None

    denominator = max(
        abs(left_value),
        abs(right_value),
        1e-12,
    )

    return round(
        clamp(
            1.0
            - abs(
                left_value
                - right_value
            )
            / denominator
        )
        * 100.0,
        2,
    )


def target_score(
    value: float | None,
    *,
    ideal_min: float,
    ideal_max: float,
    tolerance: float,
) -> float | None:
    if value is None:
        return None

    if ideal_min <= value <= ideal_max:
        return 100.0

    distance = (
        ideal_min - value
        if value < ideal_min
        else value - ideal_max
    )

    return round(
        clamp(
            1.0
            - distance / tolerance
        )
        * 100.0,
        2,
    )


def toe_direction_deg(
    *,
    heel_x: float | None,
    heel_y: float | None,
    toe_x: float | None,
    toe_y: float | None,
) -> float | None:
    if (
        heel_x is None
        or heel_y is None
        or toe_x is None
        or toe_y is None
    ):
        return None

    return round(
        degrees(
            atan2(
                toe_y - heel_y,
                toe_x - heel_x,
            )
        ),
        2,
    )


def confidence_percent(
    values: list[float],
) -> float | None:
    """
    Geometric mean of a list of [0, 1]-scaled confidence values, as a
    percentage.

    **Scale contract, audited and documented 2026-07-17 (§stride-geometry
    correction pass)**: this function assumes every input is already on a
    [0, 1] scale - `clamp()`'s default range - and will silently *saturate*
    any larger value to 1.0 rather than raise. That makes it a dangerous
    function to call with an unfamiliar data source: `FootContactEvent
    .confidence` (`stride_geometry_models.py`) is actually populated from
    `biomechanics/contact_events.py`'s `ContactEvent.confidence`, which is
    on a **0-100** scale (`min(100.0, 45.0 + prominence * 2500.0 + ...)`,
    floored at 45.0 by that formula). Calling `confidence_percent` on that
    data clamps every real value to 1.0, making the geometric mean - and
    therefore the reported "confidence" - a **mathematical constant at
    100.0%** regardless of actual input quality. This is not a
    theoretical concern: it is the confirmed root cause of
    `analyze_stride_geometry` reporting `confidence: 100.0` on real
    footage whose other metrics (crossover rate, stability score) were
    simultaneously implausible. The existing unit tests never caught this
    because their synthetic fixtures used already-0-1-scaled confidence
    values (e.g. `confidence=0.94`), which happen to survive the clamp
    unchanged - a scale mismatch invisible in tests, immediately visible
    on real data.

    Kept as-is (not made scale-adaptive) rather than silently
    "fixed" to auto-detect scale, which would just relocate the danger -
    a caller could still pass a genuinely-small-but->1 value (e.g. an
    average of `[45, 0.9]`) and get a nonsensical blended result. Callers
    MUST normalize to [0, 1] themselves before calling this. See
    `compute_geometry_confidence` below for `stride_geometry_engine.py`'s
    corrected replacement, which does not use this function on
    `FootContactEvent.confidence` directly.
    """
    bounded = [
        clamp(value)
        for value in values
    ]

    if not bounded:
        return None

    return round(
        prod(bounded)
        ** (
            1.0 / len(bounded)
        )
        * 100.0,
        2,
    )


def normalize_0_100_to_unit(value: float) -> float:
    """Converts a 0-100-scaled value (e.g. ContactEvent.confidence) into
    the [0, 1] scale `confidence_percent`/`clamp` actually expect."""
    return clamp(value / 100.0)


def compute_geometry_confidence(
    *,
    contacts_used: int,
    left_count: int,
    right_count: int,
    input_confidences_0_100: list[float],
    geometry_stability_score: float | None,
) -> float | None:
    """
    Confidence in the stride-geometry *output*, not merely whether the
    function executed - the corrected replacement for the old
    `confidence_percent(FootContactEvent.confidence)` call, which (see
    that function's docstring) was both scale-broken (always evaluated
    to 100.0 on real data) and conceptually wrong even ignoring the scale
    bug: input-detection confidence says nothing about whether the
    *derived* averages (step length, symmetry, stability) are
    statistically trustworthy.

    Four independent factors, combined by the same `weighted_score` used
    for `overall_stride_geometry_score`:

    - **Sample adequacy** (35%): averages computed from very few contacts
      are anecdotal, not statistical. Scales linearly from 0 at 4
      contacts (the hard minimum this module requires) to 100 at 20+
      contacts - chosen as a round, order-of-magnitude threshold; not
      independently calibrated against ground truth (see module-level
      limitations).
    - **Left/right sample balance** (20%): `step_length_symmetry_score`
      and the left/right averages it compares are only meaningful if
      both sides have comparable sample sizes - 3 left contacts vs 30
      right contacts makes the "left average" itself unreliable even if
      every individual detection was confident. `min(left, right) /
      max(left, right)`.
    - **Input detection confidence** (20%): the geometric mean of each
      contact's own detection confidence, correctly normalized to [0, 1]
      first this time (see `normalize_0_100_to_unit`) - still a real,
      relevant signal, just no longer the only one, and still inheriting
      whatever unreliability `contact_events.py`'s detector has (§10/§11
      of docs/ENGINEERING_HANDOFF.md - ground-contact timing is
      confirmed unreliable for some camera angles; this module has no
      way to independently verify it and does not claim to).
    - **Geometry stability** (25%): directly folds in the already-computed
      `geometry_stability_score` (coefficient-of-variation-based), so a
      numerically noisy result can no longer separately claim high
      confidence - this was the most direct way the old formula's
      100%-regardless-of-output-quality behavior manifested.

    Returns `None` only if there is nothing to compute from (empty
    input), matching the module's existing "None means not computed,
    never a fabricated number" convention.
    """
    if contacts_used <= 0:
        return None

    sample_adequacy = clamp(contacts_used / 20.0) * 100.0

    max_side = max(left_count, right_count)
    side_balance = (
        (min(left_count, right_count) / max_side) * 100.0
        if max_side > 0
        else 0.0
    )

    normalized_confidences = [
        normalize_0_100_to_unit(value)
        for value in input_confidences_0_100
    ]
    input_confidence = confidence_percent(normalized_confidences) or 0.0

    stability = (
        geometry_stability_score
        if geometry_stability_score is not None
        # Neutral, not zero: stability is unknowable (not "bad") when
        # there isn't enough same-metric variance to compute a CV from.
        else 50.0
    )

    return weighted_score(
        [
            (sample_adequacy, 0.35),
            (side_balance, 0.20),
            (input_confidence, 0.20),
            (stability, 0.25),
        ]
    )


def weighted_score(
    values: list[
        tuple[
            float | None,
            float,
        ]
    ],
) -> float | None:
    valid = [
        (
            float(value),
            float(weight),
        )
        for value, weight in values
        if value is not None
        and weight > 0.0
    ]

    if not valid:
        return None

    total_weight = sum(
        weight
        for _, weight in valid
    )

    return round(
        sum(
            value * weight
            for value, weight in valid
        )
        / total_weight,
        2,
    )


def rating_for_score(
    score: float | None,
) -> str:
    if score is None:
        return "insufficient_data"

    if score >= 90.0:
        return "excellent"
    if score >= 80.0:
        return "very_good"
    if score >= 70.0:
        return "good"
    if score >= 60.0:
        return "developing"
    if score >= 45.0:
        return "needs_improvement"

    return "poor"
