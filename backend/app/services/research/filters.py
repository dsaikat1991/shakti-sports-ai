from __future__ import annotations
from typing import Any
from app.services.research.models import ResearchRow

def filter_rows(rows: list[ResearchRow], **criteria: Any) -> list[ResearchRow]:
    result = rows
    for key, expected in criteria.items():
        if key.startswith("metadata__"):
            metadata_key = key.split("__", 1)[1]
            result = [
                row for row in result
                if (row.metadata or {}).get(metadata_key) == expected
            ]
        elif key == "minimum_confidence":
            result = [
                row for row in result
                if row.confidence is not None
                and row.confidence >= float(expected)
            ]
        else:
            result = [
                row for row in result
                if getattr(row, key) == expected
            ]
    return result
