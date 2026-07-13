from __future__ import annotations

from statistics import mean, median
from typing import Any

import numpy as np

from app.services.biomechanics.gait_event_models import (
    EventMatch,
    GaitEvent,
)


def match_events(
    predicted: list[GaitEvent],
    actual: list[GaitEvent],
    *,
    tolerance_ms: int = 80,
) -> tuple[list[EventMatch], list[GaitEvent], list[GaitEvent]]:
    """
    Greedy one-to-one matching by event type, side and nearest timestamp.

    This is intended for offline validation against manually labelled or
    instrument-derived ground truth.
    """

    remaining_actual = actual.copy()
    matches: list[EventMatch] = []
    false_positives: list[GaitEvent] = []

    for prediction in sorted(
        predicted,
        key=lambda event: event.timestamp_ms,
    ):
        candidates = [
            event
            for event in remaining_actual
            if event.event_type == prediction.event_type
            and event.side == prediction.side
        ]

        if not candidates:
            false_positives.append(prediction)
            continue

        nearest = min(
            candidates,
            key=lambda event: abs(
                event.timestamp_ms - prediction.timestamp_ms
            ),
        )

        error = abs(
            nearest.timestamp_ms - prediction.timestamp_ms
        )

        if error > tolerance_ms:
            false_positives.append(prediction)
            continue

        matches.append(
            EventMatch(
                predicted=prediction,
                actual=nearest,
                absolute_error_ms=error,
            )
        )

        remaining_actual.remove(nearest)

    false_negatives = remaining_actual

    return matches, false_positives, false_negatives


def evaluate_events(
    predicted: list[GaitEvent],
    actual: list[GaitEvent],
    *,
    tolerance_ms: int = 80,
) -> dict[str, Any]:
    matches, false_positives, false_negatives = match_events(
        predicted,
        actual,
        tolerance_ms=tolerance_ms,
    )

    true_positive_count = len(matches)
    false_positive_count = len(false_positives)
    false_negative_count = len(false_negatives)

    precision_denominator = (
        true_positive_count + false_positive_count
    )
    recall_denominator = (
        true_positive_count + false_negative_count
    )

    precision = (
        true_positive_count / precision_denominator
        if precision_denominator > 0
        else 0.0
    )

    recall = (
        true_positive_count / recall_denominator
        if recall_denominator > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    errors = [
        match.absolute_error_ms
        for match in matches
    ]

    return {
        "tolerance_ms": tolerance_ms,
        "counts": {
            "true_positives": true_positive_count,
            "false_positives": false_positive_count,
            "false_negatives": false_negative_count,
        },
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "timing_error_ms": {
            "mean_absolute_error": (
                round(mean(errors), 2)
                if errors
                else None
            ),
            "median_absolute_error": (
                round(median(errors), 2)
                if errors
                else None
            ),
            "p95_absolute_error": (
                round(
                    float(np.percentile(errors, 95)),
                    2,
                )
                if errors
                else None
            ),
            "maximum_absolute_error": (
                max(errors)
                if errors
                else None
            ),
        },
        "matches": [
            match.to_dict()
            for match in matches
        ],
        "false_positives": [
            event.to_dict()
            for event in false_positives
        ],
        "false_negatives": [
            event.to_dict()
            for event in false_negatives
        ],
    }


def evaluate_by_event_type(
    predicted: list[GaitEvent],
    actual: list[GaitEvent],
    *,
    tolerance_ms: int = 80,
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for event_type in ("initial_contact", "toe_off"):
        predicted_subset = [
            event
            for event in predicted
            if event.event_type == event_type
        ]

        actual_subset = [
            event
            for event in actual
            if event.event_type == event_type
        ]

        result[event_type] = evaluate_events(
            predicted_subset,
            actual_subset,
            tolerance_ms=tolerance_ms,
        )

    return result
