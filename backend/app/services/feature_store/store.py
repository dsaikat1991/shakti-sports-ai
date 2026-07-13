from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from app.services.feature_store.models import (
    FeatureRecord,
)
from app.services.feature_store.registry import (
    FeatureDefinitionRegistry,
)
from app.services.feature_store.validation import (
    validate_feature_value,
)


class InMemoryFeatureStore:
    """
    Development feature store.

    The interface is intentionally storage-agnostic so it can later be
    backed by Supabase/Postgres, Parquet, or a dedicated feature platform.
    """

    def __init__(
        self,
        *,
        registry: FeatureDefinitionRegistry,
    ) -> None:
        self.registry = registry
        self._records: list[
            FeatureRecord
        ] = []

    def write(
        self,
        record: FeatureRecord,
    ) -> None:
        validation = validate_feature_value(
            record.feature,
            self.registry,
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["issues"])
            )

        self._records.append(
            record
        )

    def write_many(
        self,
        records: Iterable[FeatureRecord],
    ) -> None:
        for record in records:
            self.write(record)

    def query(
        self,
        *,
        performance_id: str | None = None,
        athlete_id: str | None = None,
        event: str | None = None,
        feature_name: str | None = None,
        side: str | None = None,
        phase: str | None = None,
    ) -> list[FeatureRecord]:
        result = self._records

        if performance_id is not None:
            result = [
                record
                for record in result
                if record.performance_id == performance_id
            ]

        if athlete_id is not None:
            result = [
                record
                for record in result
                if record.athlete_id == athlete_id
            ]

        if event is not None:
            result = [
                record
                for record in result
                if record.event == event
            ]

        if feature_name is not None:
            result = [
                record
                for record in result
                if record.feature.name == feature_name
            ]

        if side is not None:
            result = [
                record
                for record in result
                if record.feature.side == side
            ]

        if phase is not None:
            result = [
                record
                for record in result
                if record.feature.phase == phase
            ]

        return list(result)

    def latest_feature_map(
        self,
        *,
        performance_id: str,
    ) -> dict[str, Any]:
        records = self.query(
            performance_id=performance_id
        )

        feature_map: dict[str, Any] = {}

        for record in records:
            feature = record.feature
            key_parts = [
                feature.name,
            ]

            if feature.side:
                key_parts.append(
                    feature.side
                )

            if feature.phase:
                key_parts.append(
                    feature.phase
                )

            key = ":".join(
                key_parts
            )

            feature_map[key] = feature.to_dict()

        return feature_map

    def athlete_history(
        self,
        *,
        athlete_id: str,
        feature_name: str,
    ) -> dict[str, list[dict[str, Any]]]:
        records = self.query(
            athlete_id=athlete_id,
            feature_name=feature_name,
        )

        grouped: dict[
            str,
            list[dict[str, Any]],
        ] = defaultdict(list)

        for record in records:
            grouped[
                record.performance_id
            ].append(
                record.feature.to_dict()
            )

        return dict(grouped)

    def size(self) -> int:
        return len(self._records)
