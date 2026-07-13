from __future__ import annotations
from statistics import mean
from typing import Any
from app.services.sprint.horizontal_force_models import HorizontalForceFrame, HorizontalForceMetrics
from app.services.sprint.horizontal_force_scoring import average_confidence, force_orientation_percent, force_vector_angle_deg, rating_for_score, score_acceleration_effectiveness, score_contact_efficiency, score_posture_alignment, score_shin_alignment, weighted_score

SUPPORTED_PHASES={'drive','transition','maximum_velocity'}

def _selected_contact_frames(frames: list[HorizontalForceFrame], *, phase: str) -> list[HorizontalForceFrame]:
    return sorted([f for f in frames if f.phase==phase and (f.ground_contact_probability is None or f.ground_contact_probability>=0.50)], key=lambda f:f.timestamp_ms)

def analyze_horizontal_force(frames: list[HorizontalForceFrame], *, phase: str) -> dict[str,Any]:
    if phase not in SUPPORTED_PHASES: return {'status':'unsupported_phase','metrics':None}
    selected=_selected_contact_frames(frames,phase=phase)
    if len(selected)<3: return {'status':'insufficient_data','metrics':None}
    h=mean(f.com_acceleration_x for f in selected); v=mean(f.com_acceleration_y for f in selected)
    orientation=force_orientation_percent(h,v); angle=force_vector_angle_deg(h,v)
    accel_score=score_acceleration_effectiveness(horizontal_acceleration=h,vertical_acceleration=v)
    trunks=[f.trunk_angle_deg for f in selected if f.trunk_angle_deg is not None]
    shins=[f.shin_angle_deg for f in selected if f.shin_angle_deg is not None]
    contacts=[f.contact_time_ms for f in selected if f.contact_time_ms is not None]
    avg_trunk=mean(trunks) if trunks else None; avg_shin=mean(shins) if shins else None; avg_contact=mean(contacts) if contacts else None
    posture=score_posture_alignment(trunk_angle_deg=avg_trunk,phase=phase)
    shin=score_shin_alignment(shin_angle_deg=avg_shin,phase=phase)
    contact=score_contact_efficiency(contact_time_ms=avg_contact,phase=phase)
    overall=weighted_score([(accel_score,0.40),(posture,0.20),(shin,0.20),(contact,0.20)])
    metrics=HorizontalForceMetrics(phase=phase,frames_used=len(selected),average_horizontal_acceleration=round(h,6),average_vertical_acceleration=round(v,6),horizontal_force_orientation_percent=orientation,mean_force_vector_angle_deg=angle,acceleration_effectiveness_score=accel_score,posture_alignment_score=posture,shin_alignment_score=shin,contact_efficiency_score=contact,overall_horizontal_force_score=overall,rating=rating_for_score(overall),confidence=average_confidence([f.confidence for f in selected]))
    evidence=[]; warnings=[]
    if orientation>=80: evidence.append('COM acceleration is strongly horizontally oriented.')
    elif orientation<60: warnings.append('COM acceleration contains a large vertical component.')
    if posture is not None and posture>=85: evidence.append('Trunk posture aligns well with the sprint phase.')
    elif posture is not None and posture<60: warnings.append('Trunk posture is outside the provisional phase target.')
    if shin is not None and shin>=85: evidence.append('Shin orientation supports horizontal projection.')
    elif shin is not None and shin<60: warnings.append('Shin orientation may limit horizontal force application.')
    if contact is not None and contact<60: warnings.append('Contact duration is outside the preferred phase range.')
    return {'status':'experimental','metrics':metrics.to_dict(),'evidence':evidence,'warnings':warnings,'method':'com_acceleration_posture_shin_contact_fusion_v0.1','validation_level':'experimental','engine_version':'0.1.0','limitations':['This engine estimates force orientation from COM acceleration and posture proxies.','It does not measure ground-reaction force.','Normalized image-space acceleration requires calibration before physical-unit claims.','Thresholds must be validated against force plates and expert-labelled sprint footage.']}

def analyze_horizontal_force_by_phase(frames: list[HorizontalForceFrame]) -> dict[str,Any]:
    phases={p:analyze_horizontal_force(frames,phase=p) for p in ('drive','transition','maximum_velocity')}
    scores=[r['metrics']['overall_horizontal_force_score'] for r in phases.values() if r['status']=='experimental' and r['metrics']['overall_horizontal_force_score'] is not None]
    return {'status':'completed' if scores else 'insufficient_data','phases':phases,'overall_phase_average_score':round(mean(scores),2) if scores else None,'engine_version':'0.1.0'}
