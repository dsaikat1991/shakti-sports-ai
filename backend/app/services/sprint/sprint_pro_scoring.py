from __future__ import annotations

from math import prod
from statistics import mean, pstdev


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def weighted_score(values: list[tuple[float | None, float]]) -> float | None:
    valid = [(float(v), float(w)) for v, w in values if v is not None and w > 0]
    if not valid:
        return None
    total = sum(w for _, w in valid)
    return round(sum(v * w for v, w in valid) / total, 2)


def target_score(
    value: float | None,
    *,
    ideal_min: float,
    ideal_max: float,
    tolerance: float,
) -> float | None:
    if value is None:
        return None
    if ideal_min <= value <= ideal_max:
        return 100.0
    distance = ideal_min - value if value < ideal_min else value - ideal_max
    return round(clamp((1.0 - distance / tolerance) * 100.0), 2)


def inverse_score(
    value: float | None,
    *,
    ideal_max: float,
    poor_max: float,
) -> float | None:
    if value is None:
        return None
    if value <= ideal_max:
        return 100.0
    if value >= poor_max:
        return 0.0
    return round((1.0 - (value - ideal_max) / (poor_max - ideal_max)) * 100.0, 2)


def cv_percent(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    avg = mean(values)
    if abs(avg) <= 1e-12:
        return None
    return float(pstdev(values) / abs(avg) * 100.0)


def confidence_percent(values: list[float | None]) -> float | None:
    valid = [max(1e-6, min(1.0, float(v))) for v in values if v is not None]
    if not valid:
        return None
    return round(prod(valid) ** (1.0 / len(valid)) * 100.0, 2)


def rating(score: float | None) -> str:
    if score is None:
        return "insufficient_data"
    if score >= 90:
        return "excellent"
    if score >= 80:
        return "very_good"
    if score >= 70:
        return "good"
    if score >= 60:
        return "developing"
    return "needs_improvement"
