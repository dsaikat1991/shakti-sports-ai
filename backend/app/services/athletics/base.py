from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.services.athletics.models import (
    EventAnalysisRequest,
    EventAnalysisResult,
)


class AthleticsEventAnalyzer(ABC):
    event_name: str = "unknown"
    analyzer_version: str = "0.1.0"

    @abstractmethod
    def analyze(
        self,
        request: EventAnalysisRequest,
        *,
        core_biomechanics: dict[str, Any],
    ) -> EventAnalysisResult:
        raise NotImplementedError
