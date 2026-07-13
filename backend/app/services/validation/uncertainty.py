from __future__ import annotations
from statistics import mean, stdev
from typing import Any
import numpy as np

def estimate_sample_uncertainty(values:list[float],*,confidence_level:float=0.95)->dict[str,Any]:
    if len(values)<2:
        return {"status":"insufficient_data","samples":len(values),"mean":values[0] if values else None,"standard_deviation":None,"standard_error":None,"confidence_interval_half_width":None,"confidence_level":confidence_level}
    m=mean(values); sd=stdev(values); se=sd/(len(values)**0.5); z=1.96 if confidence_level>=0.95 else 1.645
    return {"status":"estimated","samples":len(values),"mean":round(m,6),"standard_deviation":round(sd,6),"standard_error":round(se,6),"confidence_interval_half_width":round(z*se,6),"confidence_level":confidence_level}

def propagate_independent_uncertainty(*,partial_derivatives:list[float],input_uncertainties:list[float])->float:
    if len(partial_derivatives)!=len(input_uncertainties): raise ValueError('partial_derivatives and input_uncertainties must have equal length.')
    return round(sum((float(d)*float(u))**2 for d,u in zip(partial_derivatives,input_uncertainties))**0.5,6)

def bootstrap_uncertainty(values:list[float],*,iterations:int=1000,confidence_level:float=0.95,random_seed:int=42)->dict[str,Any]:
    if len(values)<2: return {"status":"insufficient_data","samples":len(values)}
    rng=np.random.default_rng(random_seed); arr=np.asarray(values,dtype=float)
    means=np.asarray([float(np.mean(rng.choice(arr,size=len(arr),replace=True))) for _ in range(iterations)])
    alpha=1.0-confidence_level
    lo=float(np.percentile(means,100*alpha/2)); hi=float(np.percentile(means,100*(1-alpha/2)))
    return {"status":"estimated","samples":len(values),"iterations":iterations,"mean":round(float(np.mean(arr)),6),"lower_bound":round(lo,6),"upper_bound":round(hi,6),"half_width":round((hi-lo)/2,6),"confidence_level":confidence_level}
