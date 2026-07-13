from __future__ import annotations
from app.services.research.models import ComparisonResult, ResearchRow
from app.services.research.statistics import cohens_d, describe

def compare_feature(
    *,
    feature_name: str,
    cohort_a_name: str,
    cohort_a_rows: list[ResearchRow],
    cohort_b_name: str,
    cohort_b_rows: list[ResearchRow],
) -> ComparisonResult:
    a = [
        float(row.value) for row in cohort_a_rows
        if row.feature_name == feature_name and isinstance(row.value, (int, float))
    ]
    b = [
        float(row.value) for row in cohort_b_rows
        if row.feature_name == feature_name and isinstance(row.value, (int, float))
    ]
    return ComparisonResult(
        feature_name=feature_name,
        cohort_a=cohort_a_name,
        cohort_b=cohort_b_name,
        statistics={
            "cohort_a": describe(a),
            "cohort_b": describe(b),
            "mean_difference": round(
                (sum(a) / len(a)) - (sum(b) / len(b)), 6
            ) if a and b else None,
            "cohens_d": cohens_d(a, b),
        },
    )
