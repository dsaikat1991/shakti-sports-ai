from __future__ import annotations
from typing import Iterable
from app.services.research.models import ResearchRow

class ResearchDataset:
    def __init__(self, rows: Iterable[ResearchRow] = ()) -> None:
        self._rows = list(rows)

    def add(self, row: ResearchRow) -> None:
        self._rows.append(row)

    def rows(self) -> list[ResearchRow]:
        return list(self._rows)

    def size(self) -> int:
        return len(self._rows)

    def feature_values(self, feature_name: str) -> list[float]:
        return [
            float(row.value)
            for row in self._rows
            if row.feature_name == feature_name
            and isinstance(row.value, (int, float))
        ]
