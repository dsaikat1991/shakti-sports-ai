from __future__ import annotations
from typing import Any

def reliability_gate(summary: dict[str, Any], *, minimum_average_score: float = 70.0, minimum_coverage_percent: float = 70.0) -> dict[str, Any]:
    average = summary.get("average_score")
    coverage = summary.get("coverage_above_moderate_percent")
    if not isinstance(average, (int, float)):
        return {"decision": "reject", "reason": "missing_average_score"}
    if not isinstance(coverage, (int, float)):
        return {"decision": "reject", "reason": "missing_coverage"}
    if average >= minimum_average_score and coverage >= minimum_coverage_percent:
        return {"decision": "accept", "reason": "reliability_thresholds_met"}
    if average >= minimum_average_score * 0.80 and coverage >= minimum_coverage_percent * 0.75:
        return {"decision": "downgrade", "reason": "usable_with_lower_confidence"}
    return {"decision": "reject", "reason": "reliability_below_threshold"}

def combine_landmark_gates(gates: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = [gate.get("decision") for gate in gates]
    if "reject" in decisions: decision = "reject"
    elif "downgrade" in decisions: decision = "downgrade"
    elif decisions: decision = "accept"
    else: decision = "reject"
    return {"decision": decision, "components": gates}
