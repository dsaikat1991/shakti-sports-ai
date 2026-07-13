from __future__ import annotations
from math import sqrt
from statistics import mean
from app.services.talent.models import AthleteProfileVector, SimilarityMatch
from app.services.talent.normalization import z_score_normalize

def _weighted_cosine_similarity(target: dict[str,float], candidate: dict[str,float], *, weights: dict[str,float]) -> tuple[float|None, tuple[str,...]]:
    shared=tuple(sorted(set(target)&set(candidate)))
    if len(shared)<2: return None,shared
    num=tn=cn=0.0
    for name in shared:
        w=max(0.0,float(weights.get(name,1.0))); tv=target[name]; cv=candidate[name]
        num+=w*tv*cv; tn+=w*tv*tv; cn+=w*cv*cv
    den=sqrt(tn)*sqrt(cn)
    if den<=1e-12:
        dist=sum((target[n]-candidate[n])**2 for n in shared)
        return round((1.0/(1.0+sqrt(dist)))*100.0,2),shared
    cosine=num/den; score=(cosine+1.0)/2.0
    return round(max(0.0,min(1.0,score))*100.0,2),shared

def find_similar_athletes(target: AthleteProfileVector, candidates: list[AthleteProfileVector], *, feature_weights: dict[str,float]|None=None, minimum_shared_features: int=3, top_k: int=10) -> dict:
    if not candidates: return {"status":"insufficient_data","matches":[]}
    normalized,stats=z_score_normalize([target.features,*[c.features for c in candidates]])
    nt=normalized[0]; weights=feature_weights or {}; matches=[]
    for idx,c in enumerate(candidates,start=1):
        score,shared=_weighted_cosine_similarity(nt,normalized[idx],weights=weights)
        if score is None or len(shared)<minimum_shared_features: continue
        confs=[]
        for name in shared:
            if target.confidences and name in target.confidences: confs.append(target.confidences[name])
            if c.confidences and name in c.confidences: confs.append(c.confidences[name])
        conf=round(mean(confs)*100.0,2) if confs else None
        matches.append(SimilarityMatch(c.athlete_id,score,shared,{"event":c.event,"age_group":c.age_group,"sex":c.sex,"level":c.level},conf))
    matches.sort(key=lambda m:m.similarity_score,reverse=True)
    return {"status":"completed" if matches else "insufficient_data","target_athlete_id":target.athlete_id,"event":target.event,"matches":[m.to_dict() for m in matches[:top_k]],"normalization":{"method":"cohort_z_score","feature_count":len(stats)},"engine_version":"0.1.0","limitations":["Similarity represents feature-pattern resemblance, not equivalent performance potential.","Results depend on cohort quality and feature availability.","The engine should use validated, protocol-consistent features."]}
