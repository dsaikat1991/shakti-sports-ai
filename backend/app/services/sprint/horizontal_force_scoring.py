from __future__ import annotations
from math import atan2, degrees, sqrt
from statistics import mean

def clamp(value: float, minimum: float=0.0, maximum: float=1.0) -> float:
    return max(minimum,min(maximum,float(value)))

def rating_for_score(score: float | None) -> str:
    if score is None: return 'insufficient_data'
    if score >= 90: return 'excellent'
    if score >= 80: return 'very_good'
    if score >= 70: return 'good'
    if score >= 60: return 'developing'
    if score >= 45: return 'needs_improvement'
    return 'poor'

def force_orientation_percent(horizontal_acceleration: float, vertical_acceleration: float) -> float:
    magnitude=sqrt(horizontal_acceleration**2+vertical_acceleration**2)
    if magnitude <= 1e-12: return 0.0
    return round(abs(horizontal_acceleration)/magnitude*100.0,2)

def force_vector_angle_deg(horizontal_acceleration: float, vertical_acceleration: float) -> float:
    return round(degrees(atan2(abs(vertical_acceleration),abs(horizontal_acceleration))),2)

def score_acceleration_effectiveness(*, horizontal_acceleration: float|None, vertical_acceleration: float|None) -> float|None:
    if horizontal_acceleration is None or vertical_acceleration is None: return None
    return round(clamp(force_orientation_percent(horizontal_acceleration,vertical_acceleration)/90.0)*100.0,2)

def _target_score(value: float|None, low: float, high: float, tolerance: float) -> float|None:
    if value is None: return None
    if low <= value <= high: return 100.0
    distance=low-value if value < low else value-high
    return round(clamp(1.0-distance/tolerance)*100.0,2)

def score_posture_alignment(*, trunk_angle_deg: float|None, phase: str) -> float|None:
    targets={'drive':(35.0,60.0),'transition':(55.0,78.0),'maximum_velocity':(75.0,92.0)}
    low,high=targets.get(phase,(55.0,90.0))
    return _target_score(trunk_angle_deg,low,high,30.0)

def score_shin_alignment(*, shin_angle_deg: float|None, phase: str) -> float|None:
    targets={'drive':(45.0,70.0),'transition':(55.0,78.0),'maximum_velocity':(65.0,88.0)}
    low,high=targets.get(phase,(55.0,85.0))
    return _target_score(shin_angle_deg,low,high,30.0)

def score_contact_efficiency(*, contact_time_ms: float|None, phase: str) -> float|None:
    targets={'drive':(110.0,170.0),'transition':(95.0,145.0),'maximum_velocity':(80.0,120.0)}
    low,high=targets.get(phase,(90.0,150.0))
    return _target_score(contact_time_ms,low,high,70.0)

def weighted_score(values: list[tuple[float|None,float]]) -> float|None:
    valid=[(float(v),max(0.0,float(w))) for v,w in values if v is not None and w>0]
    if not valid: return None
    total=sum(w for _,w in valid)
    if total<=0: return None
    return round(sum(v*w for v,w in valid)/total,2)

def average_confidence(values: list[float]) -> float|None:
    if not values: return None
    return round(mean(clamp(v) for v in values)*100.0,2)
