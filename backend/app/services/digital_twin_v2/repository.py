from __future__ import annotations

from typing import Protocol

from app.services.digital_twin_v2.models import TwinSession


class DigitalTwinRepository(Protocol):
    def save(self, session: TwinSession) -> None: ...

    def save_many(self, sessions: list[TwinSession]) -> None: ...

    def history(
        self,
        *,
        athlete_id: str,
        event: str | None = None,
    ) -> list[TwinSession]: ...

    def latest(
        self,
        *,
        athlete_id: str,
        event: str | None = None,
    ) -> TwinSession | None: ...


class InMemoryDigitalTwinRepository:
    def __init__(self) -> None:
        self._sessions: list[TwinSession] = []

    def save(self, session: TwinSession) -> None:
        self._sessions.append(session)

    def save_many(self, sessions: list[TwinSession]) -> None:
        for session in sessions:
            self.save(session)

    def history(
        self,
        *,
        athlete_id: str,
        event: str | None = None,
    ) -> list[TwinSession]:
        result = [
            session
            for session in self._sessions
            if session.athlete_id == athlete_id
        ]

        if event is not None:
            result = [
                session
                for session in result
                if session.event == event
            ]

        return sorted(
            result,
            key=lambda item: item.recorded_at,
        )

    def latest(
        self,
        *,
        athlete_id: str,
        event: str | None = None,
    ) -> TwinSession | None:
        history = self.history(
            athlete_id=athlete_id,
            event=event,
        )

        return history[-1] if history else None
