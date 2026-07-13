from __future__ import annotations
from statistics import mean
from typing import Any
from app.services.sprint.foot_trajectory_models import FootTrajectoryFrame,FootTrajectoryMetrics
from app.services.sprint.foot_trajectory_scoring import path_length,directness_score,cv_percent,inverse_cv_score,target_score,weighted_score,confidence_percent,rating_for_score
SUPPORTED_PHASES={'drive','transition','maximum_velocity'}

def _ordered(frames,side,phase): return sorted([f for f in frames if f.side==side and f.phase==phase],key=lambda f:(f.timestamp_ms,f.frame_index))
def _height(f): return max(max(f.hip_y,f.knee_y,f.ankle_y,f.heel_y,f.toe_y,f.com_y)-min(f.hip_y,f.knee_y,f.ankle_y,f.heel_y,f.toe_y,f.com_y),1e-6)
def _toe_clearance(f): return max(0.0,max(f.toe_y,f.heel_y)-f.toe_y)/_height(f)
def _heel_recovery(f): return max(0.0,f.hip_y-f.heel_y)/_height(f)
def _recovery_timing(frames):
    vals=[_heel_recovery(f) for f in frames]
    i=max(range(len(vals)),key=vals.__getitem__)
    return round(i/max(len(vals)-1,1)*100,2)
def _strike_score(frames):
    if len(frames)<4:return None
    tail=frames[-max(3,len(frames)//3):]
    offsets=[f.toe_x-f.com_x for f in tail]
    changes=[tail[i].toe_y-tail[i-1].toe_y for i in range(1,len(tail))]
    os=target_score(abs(mean(offsets)),0.0,0.10,0.30)
    ds=(sum(1 for v in changes if v>0)/len(changes)*100) if changes else 0.0
    return weighted_score([(os,0.6),(ds,0.4)])

def analyze_foot_trajectory(frames:list[FootTrajectoryFrame],*,side:str,phase:str)->dict[str,Any]:
    if phase not in SUPPORTED_PHASES:return {'status':'unsupported_phase','metrics':None}
    selected=_ordered(frames,side,phase)
    if len(selected)<5:return {'status':'insufficient_data','metrics':None}
    pts=[(f.toe_x,f.toe_y) for f in selected]
    max_clear=max(_toe_clearance(f) for f in selected)
    max_heel=max(_heel_recovery(f) for f in selected)
    hr=max(f.toe_x for f in selected)-min(f.toe_x for f in selected)
    plen=path_length(pts); direct=directness_score(pts); timing=_recovery_timing(selected); strike=_strike_score(selected)
    compact=target_score(hr,0.15,0.55,0.45)
    seg=[((selected[i].toe_x-selected[i-1].toe_x)**2+(selected[i].toe_y-selected[i-1].toe_y)**2)**0.5 for i in range(1,len(selected))]
    cv=cv_percent(seg); stability=inverse_cv_score(cv)
    clearance_score=target_score(max_clear,0.02,0.18,0.20)
    heel_score=target_score(max_heel,0.10,0.45,0.35)
    timing_score=target_score(timing,35.0,65.0,35.0)
    overall=weighted_score([(clearance_score,0.15),(heel_score,0.20),(direct,0.15),(timing_score,0.15),(strike,0.20),(compact,0.05),(stability,0.10)])
    conf=confidence_percent([f.confidence for f in selected])
    metrics=FootTrajectoryMetrics(side,phase,len(selected),round(max_clear,6),round(max_heel,6),round(hr,6),round(plen,6),direct,timing,strike,compact,stability,overall,rating_for_score(overall),conf)
    evidence=[]; warnings=[]
    if heel_score is not None:
        (evidence if heel_score>=85 else warnings if heel_score<60 else []).append('Heel recovery height is within the provisional target range.' if heel_score>=85 else 'Heel recovery height is outside the provisional target range.')
    if strike is not None:
        (evidence if strike>=80 else warnings if strike<60 else []).append('The foot prepares efficiently for downward strike.' if strike>=80 else 'Late-swing strike preparation is limited.')
    if direct is not None:
        (evidence if direct>=80 else warnings if direct<60 else []).append('Foot recovery path is direct and economical.' if direct>=80 else 'Foot trajectory contains excessive path deviation.')
    return {'status':'experimental','metrics':metrics.to_dict(),'evidence':evidence,'warnings':warnings,'supporting_statistics':{'trajectory_segment_cv_percent':round(cv,2) if cv is not None else None},'method':'toe_heel_recovery_path_analysis_v0.1','validation_level':'experimental','engine_version':'0.1.0','limitations':['Trajectory values are normalized image-space measurements.','Single-camera 2D analysis cannot recover true out-of-plane foot motion.','Clearance and compactness thresholds are provisional.']}

def analyze_foot_trajectory_by_phase(frames:list[FootTrajectoryFrame])->dict[str,Any]:
    results={};scores=[]
    for side in ('left','right'):
        results[side]={}
        for phase in ('drive','transition','maximum_velocity'):
            r=analyze_foot_trajectory(frames,side=side,phase=phase);results[side][phase]=r
            if r['status']=='experimental' and r['metrics']['overall_foot_trajectory_score'] is not None:scores.append(r['metrics']['overall_foot_trajectory_score'])
    return {'status':'completed' if scores else 'insufficient_data','sides':results,'overall_average_foot_trajectory_score':round(mean(scores),2) if scores else None,'engine_version':'0.1.0'}
