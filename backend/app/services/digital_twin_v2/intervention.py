from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.digital_twin_v2.models import (
    TwinSession,
)
from app.services.digital_twin_v2.statistics import (
    LOWER_IS_BETTER,
)


def evaluate_intervention_response(
    sessions: list[TwinSession],
    *,
    intervention_key: str = "intervention_id",
) -> dict[str, Any]:
    ordered = sorted(
        sessions,
        key=lambda item: item.recorded_at,
    )

    intervention_sessions = [
        session
        for session in ordered
        if session.context
        and intervention_key
        in session.context
    ]

    if not intervention_sessions:
        return {
            "status": "insufficient_data",
            "interventions": [],
        }

    results = []

    intervention_ids = sorted(
        {
            str(
                session.context[
                    intervention_key
                ]
            )
            for session in intervention_sessions
        }
    )

    for intervention_id in intervention_ids:
        matching = [
            session
            for session in ordered
            if session.context
            and str(
                session.context.get(
                    intervention_key
                )
            )
            == intervention_id
        ]

        first_index = ordered.index(
            matching[0]
        )

        before = ordered[
            max(
                0,
                first_index - 3,
            ):
            first_index
        ]

        after = matching

        feature_names = sorted(
            {
                feature_name
                for session in [
                    *before,
                    *after,
                ]
                for feature_name
                in session.features
            }
        )

        feature_changes = []

        for feature_name in feature_names:
            before_values = [
                session.features[
                    feature_name
                ]
                for session in before
                if feature_name
                in session.features
            ]

            after_values = [
                session.features[
                    feature_name
                ]
                for session in after
                if feature_name
                in session.features
            ]

            if not before_values or not after_values:
                continue

            before_mean = mean(
                before_values
            )

            after_mean = mean(
                after_values
            )

            raw_change = (
                after_mean
                - before_mean
            )

            improvement = (
                -raw_change
                if feature_name
                in LOWER_IS_BETTER
                else raw_change
            )

            feature_changes.append(
                {
                    "feature_name": feature_name,
                    "before_mean": round(
                        before_mean,
                        3,
                    ),
                    "after_mean": round(
                        after_mean,
                        3,
                    ),
                    "improvement_direction_change": (
                        round(
                            improvement,
                            3,
                        )
                    ),
                    "response": (
                        "positive"
                        if improvement > 0.0
                        else "negative"
                        if improvement < 0.0
                        else "neutral"
                    ),
                }
            )

        positive_count = sum(
            1
            for item
            in feature_changes
            if item[
                "response"
            ]
            == "positive"
        )

        response_score = (
            positive_count
            / len(
                feature_changes
            )
            * 100.0
            if feature_changes
            else None
        )

        results.append(
            {
                "intervention_id": (
                    intervention_id
                ),
                "before_sessions": len(
                    before
                ),
                "after_sessions": len(
                    after
                ),
                "response_score": (
                    round(
                        response_score,
                        2,
                    )
                    if response_score
                    is not None
                    else None
                ),
                "feature_changes": (
                    feature_changes
                ),
            }
        )

    return {
        "status": "completed",
        "interventions": results,
        "engine_version": "1.0.0",
        "validation_level": "experimental",
        "limitations": [
            "Intervention response is observational and does not establish causation.",
            "Training context, maturation, illness, and other confounders may affect the result.",
        ],
    }
