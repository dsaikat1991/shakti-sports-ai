from __future__ import annotations

from app.services.athletics.base import (
    AthleticsEventAnalyzer,
)
from app.services.athletics.high_jump import (
    HighJumpEventAnalyzer,
)
from app.services.athletics.hurdles import (
    HurdlesEventAnalyzer,
)
from app.services.athletics.long_jump import (
    LongJumpEventAnalyzer,
)
from app.services.athletics.sprint import (
    SprintEventAnalyzer,
)


class AthleticsAnalyzerRegistry:
    def __init__(self) -> None:
        self._analyzers: dict[
            str,
            AthleticsEventAnalyzer,
        ] = {}

    def register(
        self,
        analyzer: AthleticsEventAnalyzer,
    ) -> None:
        self._analyzers[
            analyzer.event_name
        ] = analyzer

    def get(
        self,
        event_name: str,
    ) -> AthleticsEventAnalyzer:
        try:
            return self._analyzers[
                event_name
            ]
        except KeyError as exc:
            raise KeyError(
                f"No athletics analyzer registered for '{event_name}'."
            ) from exc

    def available_events(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(self._analyzers)
        )


def create_default_athletics_registry(
) -> AthleticsAnalyzerRegistry:
    registry = AthleticsAnalyzerRegistry()

    registry.register(
        SprintEventAnalyzer()
    )
    registry.register(
        HurdlesEventAnalyzer()
    )
    registry.register(
        LongJumpEventAnalyzer()
    )
    registry.register(
        HighJumpEventAnalyzer()
    )

    return registry
