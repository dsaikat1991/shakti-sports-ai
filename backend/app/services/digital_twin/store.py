from __future__ import annotations

from collections import defaultdict

from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
)


class InMemoryDigitalTwinStore:
    """
    Development-only persistence layer.

    This interface can later be implemented with Supabase/Postgres
    without changing the analytics modules.
    """

    def __init__(self) -> None:
        self._snapshots: list[
            AthleteMetricSnapshot
        ] = []

    def write(
        self,
        snapshot: AthleteMetricSnapshot,
    ) -> None:
        self._snapshots.append(
            snapshot
        )

    def write_many(
        self,
        snapshots: list[AthleteMetricSnapshot],
    ) -> None:
        for snapshot in snapshots:
            self.write(snapshot)

    def athlete_history(
        self,
        *,
        athlete_id: str,
        event: str | None = None,
    ) -> list[AthleteMetricSnapshot]:
        result = [
            snapshot
            for snapshot in self._snapshots
            if snapshot.athlete_id == athlete_id
        ]

        if event is not None:
            result = [
                snapshot
                for snapshot in result
                if snapshot.event == event
            ]

        return sorted(
            result,
            key=lambda snapshot: snapshot.recorded_at,
        )

    def metric_series(
        self,
        *,
        athlete_id: str,
        metric_name: str,
        event: str | None = None,
    ) -> list[
        tuple[
            AthleteMetricSnapshot,
            float,
        ]
    ]:
        return [
            (
                snapshot,
                float(
                    snapshot.metrics[
                        metric_name
                    ]
                ),
            )
            for snapshot in self.athlete_history(
                athlete_id=athlete_id,
                event=event,
            )
            if metric_name
            in snapshot.metrics
        ]

    def latest_snapshot(
        self,
        *,
        athlete_id: str,
        event: str | None = None,
    ) -> AthleteMetricSnapshot | None:
        history = self.athlete_history(
            athlete_id=athlete_id,
            event=event,
        )

        if not history:
            return None

        return history[-1]

    def size(self) -> int:
        return len(self._snapshots)
