from __future__ import annotations

from typing import Any


def build_efficiency_explanation(
    result: dict[str, Any],
) -> dict[str, Any]:
    efficiency = result.get(
        "mechanical_efficiency",
        {}
    )

    pillars = efficiency.get(
        "pillars",
        [],
    )

    strengths: list[
        dict[str, Any]
    ] = []

    development_areas: list[
        dict[str, Any]
    ] = []

    for pillar in pillars:
        score = pillar.get(
            "score"
        )

        item = {
            "pillar": pillar.get(
                "name"
            ),
            "score": score,
            "evidence": pillar.get(
                "evidence",
                [],
            ),
            "penalties": pillar.get(
                "penalties",
                [],
            ),
        }

        if isinstance(
            score,
            (int, float),
        ) and score >= 80.0:
            strengths.append(
                item
            )

        elif isinstance(
            score,
            (int, float),
        ) and score < 70.0:
            development_areas.append(
                item
            )

    strengths.sort(
        key=lambda item: (
            item["score"]
        ),
        reverse=True,
    )

    development_areas.sort(
        key=lambda item: (
            item["score"]
        ),
    )

    return {
        "overall_score": efficiency.get(
            "score"
        ),
        "rating": efficiency.get(
            "rating"
        ),
        "confidence": efficiency.get(
            "confidence"
        ),
        "strengths": strengths,
        "development_areas": (
            development_areas
        ),
        "validation_level": (
            efficiency.get(
                "validation_level"
            )
        ),
    }
