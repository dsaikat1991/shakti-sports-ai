from __future__ import annotations
import math
from typing import Any

def combine_confidence_scores(scores:list[float|None],*,weights:list[float]|None=None,minimum_components:int=2)->float|None:
    if weights is not None and len(weights)!=len(scores): raise ValueError('weights and scores must have equal length.')
    pairs=[]
    for i,score in enumerate(scores):
        if score is None: continue
        w=float(weights[i]) if weights is not None else 1.0
        pairs.append((max(1e-6,min(1.0,float(score))),max(0.0,w)))
    if len(pairs)<minimum_components: return None
    tw=sum(w for _,w in pairs)
    if tw<=0: return None
    return round(math.exp(sum(w*math.log(s) for s,w in pairs)/tw),6)

def confidence_rating(score:float|None)->str:
    if score is None: return 'insufficient_data'
    if score>=0.90: return 'very_high'
    if score>=0.80: return 'high'
    if score>=0.65: return 'moderate'
    if score>=0.50: return 'low'
    return 'very_low'

def build_confidence_payload(*,landmark_confidence:float|None,motion_confidence:float|None,event_confidence:float|None,physics_confidence:float|None)->dict[str,Any]:
    combined=combine_confidence_scores([landmark_confidence,motion_confidence,event_confidence,physics_confidence],weights=[1.2,1.1,1.0,0.8],minimum_components=2)
    return {"score":round(combined*100,2) if combined is not None else None,"rating":confidence_rating(combined),"components":{"landmark_confidence":landmark_confidence,"motion_confidence":motion_confidence,"event_confidence":event_confidence,"physics_confidence":physics_confidence}}
