from __future__ import annotations

from typing import Any

from app.services.feature_store.models import (
    FeatureValue,
)
from app.services.feature_store.registry import (
    FeatureDefinitionRegistry,
)


def validate_feature_value(
    feature: FeatureValue,
    registry: FeatureDefinitionRegistry,
) -> dict[str, Any]:
    issues: list[str] = []

    definition = registry.get(
        feature.name
    )

    if feature.unit != definition.unit:
        issues.append(
            f"Expected unit '{definition.unit}', received '{feature.unit}'."
        )

    if feature.tier != definition.tier:
        issues.append(
            f"Expected tier '{definition.tier}', received '{feature.tier}'."
        )

    if feature.source_stage != definition.source_stage:
        issues.append(
            "Feature source_stage does not match its registered definition."
        )

    if (
        feature.confidence is not None
        and not 0.0 <= feature.confidence <= 1.0
    ):
        issues.append(
            "confidence must be between 0 and 1."
        )

    if (
        feature.uncertainty is not None
        and feature.uncertainty < 0.0
    ):
        issues.append(
            "uncertainty must not be negative."
        )

    for context_name in definition.required_context:
        if getattr(feature, context_name) is None:
            issues.append(
                f"Missing required context '{context_name}'."
            )

    return {
        "valid": not issues,
        "issues": issues,
        "definition_version": definition.version,
    }
