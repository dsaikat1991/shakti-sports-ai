from __future__ import annotations
from typing import Any
from app.services.research.statistics import describe

def build_feature_report(feature_name: str, values: list[float]) -> dict[str, Any]:
    return {
        "feature_name": feature_name,
        "summary": describe(values),
        "report_version": "0.1.0",
    }
