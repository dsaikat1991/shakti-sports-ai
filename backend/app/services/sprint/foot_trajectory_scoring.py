from __future__ import annotations
from math import hypot, prod
from statistics import mean, pstdev

def clamp(v:float,a:float=0.0,b:float=1.0)->float: return max(a,min(b,float(v)))
def path_length(points:list[tuple[float,float]])->float:
    return sum(hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]) for i in range(1,len(points)))
def directness_score(points:list[tuple[float,float]])->float|None:
    if len(points)<2:return None
    travelled=path_length(points)
    if travelled<=1e-12:return 100.0
    disp=hypot(points[-1][0]-points[0][0],points[-1][1]-points[0][1])
    return round(clamp(disp/travelled)*100,2)
def cv_percent(values:list[float])->float|None:
    if len(values)<2:return None
    m=mean(values)
    if abs(m)<=1e-12:return None
    return pstdev(values)/abs(m)*100
def inverse_cv_score(v:float|None,ideal:float=15,poor:float=60)->float|None:
    if v is None:return None
    if v<=ideal:return 100.0
    if v>=poor:return 0.0
    return round((1-(v-ideal)/(poor-ideal))*100,2)
def target_score(v:float|None,lo:float,hi:float,tol:float)->float|None:
    if v is None:return None
    if lo<=v<=hi:return 100.0
    d=lo-v if v<lo else v-hi
    return round(clamp(1-d/tol)*100,2)
def weighted_score(values:list[tuple[float|None,float]])->float|None:
    valid=[(float(v),float(w)) for v,w in values if v is not None and w>0]
    if not valid:return None
    tw=sum(w for _,w in valid)
    return round(sum(v*w for v,w in valid)/tw,2)
def confidence_percent(values:list[float])->float|None:
    if not values:return None
    vals=[clamp(v) for v in values]
    return round(prod(vals)**(1/len(vals))*100,2)
def rating_for_score(s:float|None)->str:
    if s is None:return 'insufficient_data'
    if s>=90:return 'excellent'
    if s>=80:return 'very_good'
    if s>=70:return 'good'
    if s>=60:return 'developing'
    if s>=45:return 'needs_improvement'
    return 'poor'
