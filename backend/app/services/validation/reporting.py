from __future__ import annotations
from app.services.validation.models import MetricEstimate

def classify_metric_tier(*,direct_pose_measurement:bool,model_based_estimate:bool,predictive_model_used:bool)->str:
    if predictive_model_used: return 'predictive'
    if model_based_estimate: return 'estimated'
    if direct_pose_measurement: return 'measured'
    return 'estimated'

def build_metric_estimate(*,name:str,value:float|None,unit:str|None,uncertainty:float|None,confidence:float|None,tier:str,method:str,version:str)->MetricEstimate:
    if tier not in ('measured','estimated','predictive'): raise ValueError('Invalid metric tier.')
    return MetricEstimate(name,value,unit,uncertainty,confidence,tier,method,version)
