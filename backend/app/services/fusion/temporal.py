from __future__ import annotations
from typing import Any

def smooth_probabilities(values: list[float], *, window_size: int=5)->list[float]:
    if not values: return []
    if window_size<=1: return [round(max(0.0,min(1.0,v)),6) for v in values]
    if window_size%2==0: window_size+=1
    r=window_size//2; out=[]
    for i in range(len(values)):
        w=values[max(0,i-r):min(len(values),i+r+1)]
        out.append(round(sum(w)/len(w),6))
    return out

def detect_local_peaks(probabilities: list[float], timestamps_ms: list[int], *, threshold: float, radius: int=2, minimum_gap_ms: int=60)->list[dict[str,Any]]:
    if len(probabilities)!=len(timestamps_ms): raise ValueError('probabilities and timestamps_ms must have equal length.')
    peaks=[]; last=-10000
    for i,p in enumerate(probabilities):
        if p<threshold: continue
        s=max(0,i-radius); e=min(len(probabilities),i+radius+1)
        if p<max(probabilities[s:e]): continue
        t=int(timestamps_ms[i])
        if t-last<minimum_gap_ms: continue
        peaks.append({'index':i,'timestamp_ms':t,'probability':round(p,6)}); last=t
    return peaks
