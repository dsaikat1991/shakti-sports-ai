from __future__ import annotations
import math

def logistic_probability(score: float, *, midpoint: float=0.5, steepness: float=10.0)->float:
    v=1.0/(1.0+math.exp(-steepness*(float(score)-midpoint)))
    return round(max(0.0,min(1.0,v)),6)

def noisy_or_probability(probabilities: list[float])->float:
    if not probabilities: return 0.0
    product=1.0
    for p in probabilities:
        b=max(0.0,min(1.0,float(p))); product*=1.0-b
    return round(1.0-product,6)
