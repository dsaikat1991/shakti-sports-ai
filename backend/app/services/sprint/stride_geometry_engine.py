from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.stride_geometry_models import (
    FootContactEvent,
    StrideGeometryContext,
    StrideGeometryMetrics,
)
from app.services.sprint.stride_geometry_scoring import (
    coefficient_of_variation_percent,
    confidence_percent,
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


def _step_widths(
    contacts: list[FootContactEvent],
) -> list[float]:
    values: list[float] = []

    for previous, current in zip(
        contacts,
        contacts[1:],
    ):
        if previous.side == current.side:
            continue

        values.append(
            abs(
                current.foot_y
                - previous.foot_y
            )
        )

    return values


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


def _crossover_count(
    contacts: list[FootContactEvent],
) -> int:
    count = 0

    for contact in contacts:
        if (
            contact.side == "left"
            and contact.foot_y
            > contact.com_y
        ):
            count += 1

        elif (
            contact.side == "right"
            and contact.foot_y
            < contact.com_y
        ):
            count += 1

    return count


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

    widths = _step_widths(
        ordered
    )

    offsets = _foot_offsets_percent(
        ordered,
        body_height_normalized=(
            context.body_height_normalized
        ),
    )

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

    average_width = safe_mean(
        widths
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

    average_width_m = (
        average_width * scale
        if average_width is not None
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

    crossover_contacts = (
        _crossover_count(
            ordered
        )
    )

    crossover_rate = (
        crossover_contacts
        / len(ordered)
        * 100.0
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

    width_cv = (
        coefficient_of_variation_percent(
            widths
        )
    )

    offset_cv = (
        coefficient_of_variation_percent(
            offsets
        )
    )

    geometry_stability = weighted_score(
        [
            (
                inverse_cv_score(
                    step_cv,
                    ideal_max=3.0,
                    poor_max=15.0,
                ),
                0.45,
            ),
            (
                inverse_cv_score(
                    width_cv,
                    ideal_max=5.0,
                    poor_max=25.0,
                ),
                0.25,
            ),
            (
                inverse_cv_score(
                    offset_cv,
                    ideal_max=8.0,
                    poor_max=40.0,
                ),
                0.30,
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

    width_score = target_score(
        average_width,
        ideal_min=0.01,
        ideal_max=0.12,
        tolerance=0.18,
    )

    crossover_score = max(
        0.0,
        100.0
        - crossover_rate
        * 2.0,
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

    overall = weighted_score(
        [
            (
                step_length_score,
                0.25,
            ),
            (
                foot_placement_score,
                0.20,
            ),
            (
                width_score,
                0.15,
            ),
            (
                symmetry,
                0.15,
            ),
            (
                geometry_stability,
                0.15,
            ),
            (
                crossover_score,
                0.05,
            ),
            (
                toe_direction_score,
                0.05,
            ),
        ]
    )

    confidence = confidence_percent(
        [
            contact.confidence
            for contact in ordered
        ]
    )

    metrics = StrideGeometryMetrics(
        contacts_used=len(
            ordered
        ),
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
        average_step_width_normalized=(
            round(
                average_width,
                6,
            )
            if average_width
            is not None
            else None
        ),
        average_step_width_m=(
            round(
                average_width_m,
                4,
            )
            if average_width_m
            is not None
            else None
        ),
        average_foot_offset_from_com_percent_body_height=(
            round(
                average_offset,
                2,
            )
            if average_offset
            is not None
            else None
        ),
        crossover_contacts=(
            crossover_contacts
        ),
        crossover_rate_percent=round(
            crossover_rate,
            2,
        ),
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

    if crossover_rate >= 20.0:
        warnings.append(
            "Cross-over contacts are frequent."
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
            "step_width_cv_percent": (
                round(
                    width_cv,
                    2,
                )
                if width_cv
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
            "alternating_contact_geometry_v0.1"
        ),
        "validation_level": "experimental",
        "engine_version": "0.1.0",
        "limitations": [
            "Uncalibrated outputs are normalized image-space measurements.",
            "Absolute metres are only reported when a real-world scale is supplied.",
            "The optimal step-length estimate is provisional and should not be treated as an individual prescription.",
            "Toe direction from a single 2D view is a coarse image-plane estimate.",
            "Cross-over detection depends on camera alignment and COM estimation.",
        ],
    }
