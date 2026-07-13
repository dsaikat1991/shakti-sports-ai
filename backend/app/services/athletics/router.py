from __future__ import annotations

from typing import Any

from app.services.athletics.models import (
    EventAnalysisRequest,
)
from app.services.athletics.registry import (
    AthleticsAnalyzerRegistry,
    create_default_athletics_registry,
)


def analyze_athletics_event(
    request: EventAnalysisRequest,
    *,
    core_biomechanics: dict[str, Any],
    registry: AthleticsAnalyzerRegistry | None = None,
) -> dict[str, Any]:
    active_registry = (
        registry
        or create_default_athletics_registry()
    )

    analyzer = active_registry.get(
        request.event
    )

    result = analyzer.analyze(
        request,
        core_biomechanics=core_biomechanics,
    )

    return result.to_dict()
