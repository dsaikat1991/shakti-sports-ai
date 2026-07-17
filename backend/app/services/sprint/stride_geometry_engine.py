"""
Stride geometry - per-contact spatial analysis (step length, symmetry,
foot placement relative to centre of mass, stride stability) from a
sequence of ground-contact events.

**Status (as of the 2026-07-17 §stride-geometry correction pass, see
docs/ENGINEERING_HANDOFF.md): IMPLEMENTED BUT UNWIRED, algorithm
correctness improved, still NOT integrated into the live API.** This
module was never part of the live `/api/analyze/video` pipeline (see
Milestone B's audit in the handoff doc) - this pass is algorithm
correction, not integration. Nothing in `app/api/` or `app/main.py`
calls this module before or after this pass.

**Coordinate system (see `FootContactEvent`'s docstring for the full
reasoning)**: every input is a normalized 2D image-space coordinate from
a side-view camera. X is a genuine proxy for along-track (direction-of-
travel) distance; Y is a genuine proxy for height off the ground. The
true mediolateral (left-right) axis is oriented along the camera's line
of sight in a side-view shot and is **not observable in this
projection**. `step_length`, `stride_length`, and
`foot_offset_from_com` are all X-axis-based and measure what they claim
to measure. `crossover_rate_percent` and `average_step_width_*` are
**not computed** (`None`, with an explicit reason) as of this pass - a
prior version computed them from Y-axis (vertical) comparisons, which
does not correspond to lateral separation at all and produced
implausible values on real footage (a confirmed axis-selection bug,
see this module's audit report). See `LATERAL_METRICS_UNAVAILABLE_REASON`
in `stride_geometry_models.py`.

**Dependency chain and inherited uncertainty**: every metric in this
module is downstream of `biomechanics/contact_events.py`'s ground-
contact detector, which is **confirmed unreliable for some camera
angles** (§10/§11 of docs/ENGINEERING_HANDOFF.md - a hand-labeled
counterexample showed a true contact scoring lower on the detector's
own confidence signal than a confirmed false positive). This module has
no independent way to verify contact timing and does not claim to -
`confidence` (see `compute_geometry_confidence`) partially reflects
this by weighting in the contact detector's own per-event confidence,
but a systematically-biased-yet-individually-confident set of false
contacts would not be caught by that alone. Wrong contacts in -> wrong
geometry out, regardless of how this module scores itself.

**Maturity classification** (per-metric, not module-wide - see this
module's audit report for the full table):
- **Plausibility-tested against real footage**: step length, stride
  length, foot-offset-from-COM, step-length symmetry (re-run against
  `my_sprint_2.mp4` after this correction pass, see the audit report's
  Phase 4 - values now fall in ranges consistent with the athlete's own
  independently-computed cadence, unlike before this pass).
- **Experimental, not yet plausibility-tested**: toe direction
  (in/neutral/out classification), optimal-step-length heuristic (the
  1.15x-leg-length rule of thumb is a commonly-cited approximation in
  running-form literature, not independently validated here).
- **Not computable, not attempted**: crossover, true step width (lateral
  plane, unobservable from this camera configuration - see above).
- **Nothing in this module is ground-truth validated** - no hand-labeled
  stride-geometry dataset exists (unlike ground-contact timing, which
  has one, §10). "Plausibility-tested" means outputs were checked for
  internal consistency and physiological reasonableness against known
  facts about the same clip (e.g. independently-computed cadence) - it
  is a lower bar than ground-truth validation and should not be
  conflated with it.
"""

from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.stride_geometry_models import (
    LATERAL_METRICS_UNAVAILABLE_REASON,
    FootContactEvent,
    StrideGeometryContext,
    StrideGeometryMetrics,
)
from app.services.sprint.stride_geometry_scoring import (
    coefficient_of_variation_percent,
    compute_geometry_confidence,
    inverse_cv_score,
    rating_for_score,
    safe_mean,
    symmetry_score,
    target_score,
    toe_direction_deg,
    weighted_score,
)


def _ordered_contacts(
    contacts: list[FootContactEvent],
) -> list[FootContactEvent]:
    return sorted(
        contacts,
        key=lambda item: (
            item.timestamp_ms,
            item.frame_index,
        ),
    )


def _step_lengths_by_landing_side(
    contacts: list[FootContactEvent],
) -> dict[str, list[float]]:
    result = {
        "left": [],
        "right": [],
    }

    for previous, current in zip(
        contacts,
        contacts[1:],
    ):
        if previous.side == current.side:
            continue

        length = abs(
            current.foot_x
            - previous.foot_x
        )

        result[
            current.side
        ].append(
            float(length)
        )

    return result


def _stride_lengths(
    contacts: list[FootContactEvent],
) -> list[float]:
    values: list[float] = []

    for index in range(
        2,
        len(contacts),
    ):
        current = contacts[index]
        previous_same_side = (
            contacts[index - 2]
        )

        if (
            current.side
            != previous_same_side.side
        ):
            continue

        values.append(
            abs(
                current.foot_x
                - previous_same_side.foot_x
            )
        )

    return values


# _step_widths (previously here) was removed in the 2026-07-17
# §stride-geometry correction pass. It computed abs(Y_a - Y_b) between
# consecutive alternating-side contacts and reported the result as "step
# width" - but Y is the image-vertical (height-off-ground) axis in this
# side-view coordinate system, and true step width is a mediolateral
# (left-right) quantity this camera configuration cannot observe (see
# this module's docstring and FootContactEvent's). The removed
# function's output was foot-height difference at alternating contacts,
# not lateral separation - a different physical quantity with no
# established biomechanical meaning under that name. See
# LATERAL_METRICS_UNAVAILABLE_REASON.


def _foot_offsets_percent(
    contacts: list[FootContactEvent],
    *,
    body_height_normalized: float | None,
) -> list[float]:
    denominator = (
        body_height_normalized
        if body_height_normalized
        is not None
        and body_height_normalized
        > 1e-12
        else 1.0
    )

    return [
        (
            contact.foot_x
            - contact.com_x
        )
        / denominator
        * 100.0
        for contact in contacts
    ]


# _crossover_count (previously here) was removed in the 2026-07-17
# §stride-geometry correction pass - this was the confirmed axis-
# selection bug found during the stride-geometry audit. It compared
# contact.foot_y ("left" side) or the reverse ("right" side) against
# contact.com_y - i.e. it compared VERTICAL (image-Y, height-off-ground)
# positions and called the result "crossover". Crossover is a lateral
# (mediolateral, left-right) phenomenon - a foot landing across the
# body's midline toward or past the opposite side - which is a
# fundamentally different, unrelated axis from foot height. On real
# footage (my_sprint_2.mp4, 46 contacts) this produced
# crossover_rate_percent = 47.83%, physiologically implausible for any
# real running gait (a true crossover on every other step is not a
# pattern healthy sprinters produce) - strong evidence the formula was
# measuring noise/an unrelated quantity, not a real gait fault. The
# right fix is not a different formula on the same two axes - true
# lateral separation is not observable from a single side-view 2D
# camera at all (see this module's docstring) - so this is now reported
# as unavailable rather than replaced with a different guess. See
# LATERAL_METRICS_UNAVAILABLE_REASON.


def _toe_direction_counts(
    contacts: list[FootContactEvent],
) -> tuple[
    int,
    int,
    int,
]:
    toe_in = 0
    neutral = 0
    toe_out = 0

    for contact in contacts:
        angle = toe_direction_deg(
            heel_x=contact.heel_x,
            heel_y=contact.heel_y,
            toe_x=contact.toe_x,
            toe_y=contact.toe_y,
        )

        if angle is None:
            continue

        signed_angle = angle

        if contact.side == "left":
            signed_angle *= -1.0

        if signed_angle < -12.0:
            toe_in += 1
        elif signed_angle > 12.0:
            toe_out += 1
        else:
            neutral += 1

    return (
        toe_in,
        neutral,
        toe_out,
    )


def _optimal_step_length(
    *,
    average_step_length: float | None,
    cadence_spm: float | None,
    horizontal_velocity: float | None,
    leg_length_normalized: float | None,
) -> float | None:
    candidates: list[float] = []

    if (
        cadence_spm is not None
        and cadence_spm > 1e-12
        and horizontal_velocity is not None
    ):
        step_frequency_hz = (
            cadence_spm / 60.0
        )

        candidates.append(
            abs(
                horizontal_velocity
            )
            / step_frequency_hz
        )

    if (
        leg_length_normalized is not None
        and leg_length_normalized
        > 1e-12
    ):
        candidates.append(
            leg_length_normalized
            * 1.15
        )

    if not candidates:
        return average_step_length

    return mean(candidates)


def analyze_stride_geometry(
    contacts: list[FootContactEvent],
    *,
    context: StrideGeometryContext,
    cadence_spm: float | None = None,
    horizontal_velocity: float | None = None,
) -> dict[str, Any]:
    ordered = _ordered_contacts(
        contacts
    )

    if len(ordered) < 4:
        return {
            "status": "insufficient_data",
            "metrics": None,
        }

    step_lengths = (
        _step_lengths_by_landing_side(
            ordered
        )
    )

    left_steps = step_lengths[
        "left"
    ]

    right_steps = step_lengths[
        "right"
    ]

    all_steps = [
        *left_steps,
        *right_steps,
    ]

    strides = _stride_lengths(
        ordered
    )

    offsets = _foot_offsets_percent(
        ordered,
        body_height_normalized=(
            context.body_height_normalized
        ),
    )

    left_count = sum(1 for contact in ordered if contact.side == "left")
    right_count = sum(1 for contact in ordered if contact.side == "right")

    left_average = safe_mean(
        left_steps
    )

    right_average = safe_mean(
        right_steps
    )

    average_step = safe_mean(
        all_steps
    )

    average_stride = safe_mean(
        strides
    )

    average_offset = safe_mean(
        offsets
    )

    scale = (
        context.real_world_scale_m_per_unit
    )

    average_step_m = (
        average_step * scale
        if average_step is not None
        and scale is not None
        else None
    )

    average_stride_m = (
        average_stride * scale
        if average_stride is not None
        and scale is not None
        else None
    )

    leg_ratio = (
        average_step
        / context.leg_length_normalized
        if average_step is not None
        and context.leg_length_normalized
        is not None
        and context.leg_length_normalized
        > 1e-12
        else None
    )

    optimal = _optimal_step_length(
        average_step_length=average_step,
        cadence_spm=cadence_spm,
        horizontal_velocity=(
            horizontal_velocity
        ),
        leg_length_normalized=(
            context.leg_length_normalized
        ),
    )

    difference_percent = (
        (
            average_step - optimal
        )
        / optimal
        * 100.0
        if average_step is not None
        and optimal is not None
        and abs(optimal) > 1e-12
        else None
    )

    toe_in, neutral, toe_out = (
        _toe_direction_counts(
            ordered
        )
    )

    symmetry = symmetry_score(
        left_average,
        right_average,
    )

    step_cv = (
        coefficient_of_variation_percent(
            all_steps
        )
    )

    offset_cv = (
        coefficient_of_variation_percent(
            offsets
        )
    )

    # geometry_stability_score: rebalanced in the 2026-07-17
    # §stride-geometry correction pass. width_cv's 25% weight was
    # removed along with _step_widths (see above, and this module's
    # docstring) - redistributed across the two remaining, axis-correct
    # components (60/40) rather than left orphaned or silently dropped.
    geometry_stability = weighted_score(
        [
            (
                inverse_cv_score(
                    step_cv,
                    ideal_max=3.0,
                    poor_max=15.0,
                ),
                0.60,
            ),
            (
                inverse_cv_score(
                    offset_cv,
                    ideal_max=8.0,
                    poor_max=40.0,
                ),
                0.40,
            ),
        ]
    )

    step_length_score = target_score(
        abs(
            difference_percent
        )
        if difference_percent
        is not None
        else None,
        ideal_min=0.0,
        ideal_max=5.0,
        tolerance=20.0,
    )

    foot_placement_score = target_score(
        abs(
            average_offset
        )
        if average_offset
        is not None
        else None,
        ideal_min=0.0,
        ideal_max=10.0,
        tolerance=30.0,
    )

    toe_direction_total = (
        toe_in
        + neutral
        + toe_out
    )

    toe_direction_score = (
        neutral
        / toe_direction_total
        * 100.0
        if toe_direction_total > 0
        else None
    )

    # overall_stride_geometry_score: rebalanced in the 2026-07-17
    # §stride-geometry correction pass. width_score (15%) and
    # crossover_score (5%) were removed along with the metrics they
    # scored - the remaining 80% of weight is redistributed
    # proportionally across the five components that survived
    # correction (0.25/0.80, 0.20/0.80, 0.15/0.80, 0.15/0.80, 0.05/0.80),
    # rounded to clean values summing to 1.0.
    overall = weighted_score(
        [
            (
                step_length_score,
                0.30,
            ),
            (
                foot_placement_score,
                0.25,
            ),
            (
                symmetry,
                0.20,
            ),
            (
                geometry_stability,
                0.20,
            ),
            (
                toe_direction_score,
                0.05,
            ),
        ]
    )

    # confidence: replaced in the 2026-07-17 §stride-geometry correction
    # pass. The old confidence_percent(FootContactEvent.confidence) call
    # both mis-scaled its input (see confidence_percent's docstring - it
    # silently clamped every real 0-100-scaled value to 1.0, making the
    # result a mathematical constant of 100.0%) and only ever measured
    # input-detection confidence, never output reliability.
    # compute_geometry_confidence folds in sample adequacy, left/right
    # sample balance, and the already-computed geometry_stability_score
    # alongside a correctly-normalized version of the same input signal.
    confidence = compute_geometry_confidence(
        contacts_used=len(ordered),
        left_count=left_count,
        right_count=right_count,
        input_confidences_0_100=[
            contact.confidence
            for contact in ordered
        ],
        geometry_stability_score=geometry_stability,
    )

    metrics = StrideGeometryMetrics(
        contacts_used=len(
            ordered
        ),
        left_contacts_used=left_count,
        right_contacts_used=right_count,
        left_step_length_normalized=(
            round(
                left_average,
                6,
            )
            if left_average
            is not None
            else None
        ),
        right_step_length_normalized=(
            round(
                right_average,
                6,
            )
            if right_average
            is not None
            else None
        ),
        average_step_length_normalized=(
            round(
                average_step,
                6,
            )
            if average_step
            is not None
            else None
        ),
        average_stride_length_normalized=(
            round(
                average_stride,
                6,
            )
            if average_stride
            is not None
            else None
        ),
        average_step_length_m=(
            round(
                average_step_m,
                4,
            )
            if average_step_m
            is not None
            else None
        ),
        average_stride_length_m=(
            round(
                average_stride_m,
                4,
            )
            if average_stride_m
            is not None
            else None
        ),
        normalized_step_length_leg_ratio=(
            round(
                leg_ratio,
                4,
            )
            if leg_ratio
            is not None
            else None
        ),
        expected_optimal_step_length_normalized=(
            round(
                optimal,
                6,
            )
            if optimal
            is not None
            else None
        ),
        optimal_step_length_difference_percent=(
            round(
                difference_percent,
                2,
            )
            if difference_percent
            is not None
            else None
        ),
        average_step_width_normalized=None,
        average_step_width_m=None,
        lateral_metrics_unavailable_reason=LATERAL_METRICS_UNAVAILABLE_REASON,
        average_foot_offset_from_com_percent_body_height=(
            round(
                average_offset,
                2,
            )
            if average_offset
            is not None
            else None
        ),
        crossover_contacts=None,
        crossover_rate_percent=None,
        toe_in_contacts=toe_in,
        neutral_toe_contacts=neutral,
        toe_out_contacts=toe_out,
        step_length_symmetry_score=(
            symmetry
        ),
        geometry_stability_score=(
            geometry_stability
        ),
        overall_stride_geometry_score=(
            overall
        ),
        rating=rating_for_score(
            overall
        ),
        confidence=confidence,
    )

    evidence: list[str] = []
    warnings: list[str] = []

    if symmetry is not None:
        if symmetry >= 90.0:
            evidence.append(
                "Left and right step lengths are highly symmetrical."
            )
        elif symmetry < 75.0:
            warnings.append(
                "Step-length asymmetry is substantial."
            )

    if min(left_count, right_count) < 4:
        warnings.append(
            f"Left/right sample sizes are imbalanced ({left_count} left, {right_count} right "
            "contacts) - averages and the symmetry score above are less statistically reliable "
            "with this few same-side samples, and this is already reflected in a lower confidence "
            "score."
        )

    if (
        average_offset is not None
        and abs(
            average_offset
        ) <= 10.0
    ):
        evidence.append(
            "Foot placement is close to the COM."
        )
    elif (
        average_offset is not None
        and average_offset > 20.0
    ):
        warnings.append(
            "Average landing position is ahead of the COM and may increase braking."
        )

    if geometry_stability is not None:
        if geometry_stability >= 85.0:
            evidence.append(
                "Stride geometry remains stable across contacts."
            )
        elif geometry_stability < 60.0:
            warnings.append(
                "Stride geometry varies substantially across contacts."
            )

    if (
        difference_percent is not None
        and abs(
            difference_percent
        ) <= 5.0
    ):
        evidence.append(
            "Observed step length is close to the provisional optimal estimate."
        )

    return {
        "status": "experimental",
        "metrics": metrics.to_dict(),
        "evidence": evidence,
        "warnings": warnings,
        "supporting_statistics": {
            "step_length_cv_percent": (
                round(
                    step_cv,
                    2,
                )
                if step_cv
                is not None
                else None
            ),
            "foot_offset_cv_percent": (
                round(
                    offset_cv,
                    2,
                )
                if offset_cv
                is not None
                else None
            ),
        },
        "method": (
            "alternating_contact_geometry_v0.2"
        ),
        "validation_level": "experimental",
        "engine_version": "0.2.0",
        "metric_maturity": {
            "plausibility_tested_against_real_footage": [
                "average_step_length_normalized",
                "average_stride_length_normalized",
                "average_foot_offset_from_com_percent_body_height",
                "step_length_symmetry_score",
                "geometry_stability_score",
            ],
            "experimental_not_yet_plausibility_tested": [
                "toe_in_contacts",
                "neutral_toe_contacts",
                "toe_out_contacts",
                "expected_optimal_step_length_normalized",
                "optimal_step_length_difference_percent",
                "confidence",
            ],
            "not_computable_from_this_camera_configuration": [
                "average_step_width_normalized",
                "average_step_width_m",
                "crossover_contacts",
                "crossover_rate_percent",
            ],
            "ground_truth_validated": [],
        },
        "limitations": [
            "Uncalibrated outputs are normalized image-space measurements.",
            "Absolute metres are only reported when a real-world scale is supplied.",
            "The optimal step-length estimate is provisional (a commonly-cited leg-length heuristic, not independently validated here) and should not be treated as an individual prescription.",
            "Toe direction from a single 2D view is a coarse image-plane estimate and cannot distinguish true foot rotation from the leg's swing angle at the contact instant.",
            "Crossover and true (mediolateral) step width are not computed as of the 2026-07-17 correction pass - not observable from a single side-view 2D camera. "
            + LATERAL_METRICS_UNAVAILABLE_REASON,
            "Every metric here is downstream of contact_events.py's ground-contact detector, which is confirmed unreliable for some camera angles (docs/ENGINEERING_HANDOFF.md §10/§11) - wrong contact timing in, wrong geometry out, regardless of how this module scores its own confidence.",
            "Nothing in this module is ground-truth validated (no hand-labeled stride-geometry dataset exists). 'Plausibility-tested' (see metric_maturity above) means outputs were checked for internal consistency and physiological reasonableness on real footage - a lower bar than ground-truth validation.",
        ],
    }
