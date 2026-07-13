from __future__ import annotations
from statistics import mean, median, stdev
from typing import Any
import math
import numpy as np

def describe(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"status": "insufficient_data", "n": 0}
    ordered = sorted(float(v) for v in values)
    return {
        "status": "completed",
        "n": len(ordered),
        "mean": round(mean(ordered), 6),
        "median": round(median(ordered), 6),
        "standard_deviation": round(stdev(ordered), 6) if len(ordered) > 1 else 0.0,
        "minimum": round(ordered[0], 6),
        "maximum": round(ordered[-1], 6),
        "iqr": round(float(np.percentile(ordered, 75) - np.percentile(ordered, 25)), 6),
    }

def cohens_d(group_a: list[float], group_b: list[float]) -> float | None:
    if len(group_a) < 2 or len(group_b) < 2:
        return None
    n1, n2 = len(group_a), len(group_b)
    s1, s2 = stdev(group_a), stdev(group_b)
    pooled = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    if pooled <= 1e-12:
        return 0.0
    return round((mean(group_a) - mean(group_b)) / pooled, 6)

def pearson_correlation(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return None
    return round(float(np.corrcoef(x, y)[0, 1]), 6)

def bland_altman(pairs_a: list[float], pairs_b: list[float]) -> dict[str, Any]:
    if len(pairs_a) != len(pairs_b) or len(pairs_a) < 2:
        return {"status": "insufficient_data"}
    differences = [a - b for a, b in zip(pairs_a, pairs_b)]
    bias = mean(differences)
    sd = stdev(differences)
    return {
        "status": "completed",
        "bias": round(bias, 6),
        "lower_limit": round(bias - 1.96 * sd, 6),
        "upper_limit": round(bias + 1.96 * sd, 6),
    }
