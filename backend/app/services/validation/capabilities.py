from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Literal
CameraMode = Literal["single_camera_2d","single_camera_calibrated","multi_camera"]
MetricTier = Literal["measured","estimated","predictive"]
SupportStatus = Literal["supported","conditionally_supported","unsupported"]
@dataclass(slots=True,frozen=True)
class MetricCapability:
    metric_name:str; tier:MetricTier; support_status:SupportStatus
    supported_events:tuple[str,...]; required_camera_views:tuple[str,...]
    minimum_fps:float; minimum_landmark_confidence:float
    requires_scene_calibration:bool; requires_multi_camera:bool
    requires_force_reference:bool; explanation:str; limitations:tuple[str,...]
    version:str="0.1.0"
    def to_dict(self)->dict[str,Any]:
        d=asdict(self); d["supported_events"]=list(self.supported_events); d["required_camera_views"]=list(self.required_camera_views); d["limitations"]=list(self.limitations); return d
DEFAULT_CAPABILITIES={
"joint_angle_2d":MetricCapability("joint_angle_2d","measured","supported",("sprint","hurdles","long_jump","high_jump"),("Side View",),25.0,0.70,False,False,False,"Projected image-plane angle from visible keypoints.",( "Not a true 3D joint angle.","Sensitive to camera perspective.")),
"cadence":MetricCapability("cadence","estimated","conditionally_supported",("sprint","hurdles"),("Side View",),30.0,0.75,False,False,False,"Estimated from repeated gait events.",( "Requires multiple reliable steps.",)),
"ground_contact_time":MetricCapability("ground_contact_time","estimated","conditionally_supported",("sprint","hurdles"),("Side View",),60.0,0.80,False,False,True,"Image-based estimate from gait-event fusion.",( "Not force-plate measured.","30 fps may be insufficient for precision.")),
"flight_time":MetricCapability("flight_time","estimated","conditionally_supported",("sprint","hurdles"),("Side View",),60.0,0.80,False,False,True,"Estimated between toe-off and next contact.",( "Inherits contact-event uncertainty.",)),
"stride_length":MetricCapability("stride_length","estimated","conditionally_supported",("sprint","hurdles","long_jump"),("Side View",),30.0,0.75,True,False,False,"Requires a calibrated scene distance.",( "Cannot report metres from uncalibrated coordinates.",)),
"knee_valgus":MetricCapability("knee_valgus","estimated","unsupported",(),(),60.0,0.90,True,True,False,"Reliable assessment requires calibrated 3D or multi-camera capture.",( "Unsupported from a single side-view camera.",)),
"normalized_power_proxy":MetricCapability("normalized_power_proxy","estimated","conditionally_supported",("sprint","hurdles","long_jump","high_jump"),("Side View",),60.0,0.80,False,False,True,"Camera-relative mass-normalized power proxy.",( "Not a direct watt measurement.",))}
class CapabilityRegistry:
    def __init__(self): self._items={}
    def register(self,c): self._items[c.metric_name]=c
    def get(self,name):
        if name not in self._items: raise KeyError(f"Metric capability '{name}' is not registered.")
        return self._items[name]
    def list_metrics(self): return tuple(sorted(self._items))
    def evaluate(self,metric_name:str,*,event:str,camera_view:str,camera_mode:CameraMode,fps:float,landmark_confidence:float,scene_calibrated:bool,force_reference_available:bool)->dict[str,Any]:
        c=self.get(metric_name); reasons=[]
        if c.support_status=="unsupported": reasons.append("Metric is unsupported in the current analysis mode.")
        if c.supported_events and event not in c.supported_events: reasons.append(f"Metric is not supported for event '{event}'.")
        if c.required_camera_views and camera_view not in c.required_camera_views: reasons.append("Required camera view is not satisfied.")
        if fps<c.minimum_fps: reasons.append(f"Minimum FPS is {c.minimum_fps:.0f}.")
        if landmark_confidence<c.minimum_landmark_confidence: reasons.append("Landmark confidence is below threshold.")
        if c.requires_scene_calibration and not scene_calibrated: reasons.append("Scene calibration is required.")
        if c.requires_multi_camera and camera_mode!="multi_camera": reasons.append("Multi-camera capture is required.")
        warning=None
        if c.requires_force_reference and not force_reference_available: warning="Metric may be estimated, but no force-plate or equivalent reference is available for validation."
        return {"metric":c.to_dict(),"available":not reasons,"decision":"allow" if not reasons else "block","reasons":reasons,"validation_warning":warning}
def create_default_capability_registry():
    r=CapabilityRegistry(); [r.register(c) for c in DEFAULT_CAPABILITIES.values()]; return r
