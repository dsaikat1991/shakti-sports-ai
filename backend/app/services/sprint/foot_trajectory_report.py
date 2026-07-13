from __future__ import annotations
from typing import Any

def build_foot_trajectory_report(result:dict[str,Any])->dict[str,Any]:
    m=result.get('metrics')
    if not m:return {'status':'insufficient_data'}
    return {'status':'completed','headline':f"Foot trajectory score: {m.get('overall_foot_trajectory_score')}",'summary':{'heel_recovery_height':m.get('maximum_heel_recovery_height_normalized'),'trajectory_directness_score':m.get('trajectory_directness_score'),'recovery_timing_percent':m.get('recovery_timing_percent'),'strike_preparation_score':m.get('strike_preparation_score')},'evidence':result.get('evidence',[]),'warnings':result.get('warnings',[]),'validation_level':result.get('validation_level'),'engine_version':result.get('engine_version')}
