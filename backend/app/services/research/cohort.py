from __future__ import annotations
from app.services.research.filters import filter_rows
from app.services.research.models import CohortDefinition, ResearchRow

def build_cohort(
    rows: list[ResearchRow],
    definition: CohortDefinition,
) -> list[ResearchRow]:
    return filter_rows(rows, **definition.filters)
