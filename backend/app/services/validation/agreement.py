from __future__ import annotations
from statistics import mean
from typing import Any

def coefficient_of_variation(values:list[float])->float|None:
    if len(values)<2: return None
    m=mean(values)
    if abs(m)<=1e-9: return None
    var=mean([(x-m)**2 for x in values])
    return round(abs((var**0.5)/m),6)

def typical_error(paired_differences:list[float])->float|None:
    if len(paired_differences)<2: return None
    m=mean(paired_differences); var=sum((x-m)**2 for x in paired_differences)/(len(paired_differences)-1)
    return round((var**0.5)/(2**0.5),6)

def compare_repeated_runs(runs:list[list[float]])->dict[str,Any]:
    if len(runs)<2: return {"status":"insufficient_data"}
    run_means=[mean(r) for r in runs if r]
    if len(run_means)<2: return {"status":"insufficient_data"}
    diffs=[run_means[i]-run_means[i-1] for i in range(1,len(run_means))]
    return {"status":"completed","runs":len(run_means),"run_means":[round(v,6) for v in run_means],"coefficient_of_variation":coefficient_of_variation(run_means),"typical_error":typical_error(diffs)}
