from __future__ import annotations
from statistics import mean
from typing import Any
from app.services.validation.confidence import combine_confidence_scores, confidence_rating
from app.services.validation.models import ReliabilitySummary

def summarize_pipeline_reliability(*,pose_scores:list[float],motion_scores:list[float],event_scores:list[float],physics_scores:list[float])->ReliabilitySummary:
    def avg(v): return max(0.0,min(1.0,mean(v))) if v else None
    pose,motion,event,physics=avg(pose_scores),avg(motion_scores),avg(event_scores),avg(physics_scores)
    overall=combine_confidence_scores([pose,motion,event,physics],weights=[1.25,1.15,1.0,0.75],minimum_components=2)
    return ReliabilitySummary(pose,motion,event,physics,overall,confidence_rating(overall))

def metric_stability(values:list[float])->dict[str,Any]:
    if len(values)<2: return {"status":"insufficient_data"}
    m=mean(values); drift=values[-1]-values[0]
    cv=None
    if abs(m)>1e-9:
        var=mean([(x-m)**2 for x in values]); cv=abs((var**0.5)/m)
    return {"status":"completed","mean":round(m,6),"drift":round(drift,6),"coefficient_of_variation":round(cv,6) if cv is not None else None}
