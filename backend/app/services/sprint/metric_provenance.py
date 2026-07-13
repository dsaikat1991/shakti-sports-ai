from __future__ import annotations

from typing import Any


def build_metric_provenance(
    *,
    metric_name: str,
    value: float | None,
    confidence: float | None,
    inputs: list[str],
    algorithm: str,
    validation_status: str,
    unit: str | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "metric": metric_name,
        "value": value,
        "unit": unit,
        "confidence": confidence,
        "inputs": inputs,
        "algorithm": algorithm,
        "validation_status": (
            validation_status
        ),
        "limitations": (
            limitations
            or []
        ),
    }
