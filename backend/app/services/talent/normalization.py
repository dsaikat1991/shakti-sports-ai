from __future__ import annotations
from statistics import mean, pstdev

def z_score_normalize(profiles: list[dict[str,float]]) -> tuple[list[dict[str,float]], dict[str,dict[str,float]]]:
    names=sorted({n for p in profiles for n in p})
    stats={}
    for name in names:
        values=[p[name] for p in profiles if name in p]
        stats[name]={"mean":float(mean(values)),"std":float(pstdev(values))}
    normalized=[]
    for p in profiles:
        row={}
        for name,value in p.items():
            avg=stats[name]["mean"]; std=stats[name]["std"]
            row[name]=0.0 if std<=1e-12 else (float(value)-avg)/std
        normalized.append(row)
    return normalized,stats

def apply_z_score(features: dict[str,float], stats: dict[str,dict[str,float]]) -> dict[str,float]:
    result={}
    for name,value in features.items():
        if name not in stats: continue
        avg=stats[name]["mean"]; std=stats[name]["std"]
        result[name]=0.0 if std<=1e-12 else (float(value)-avg)/std
    return result
