from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Literal
LightingCondition=Literal["bright_daylight","overcast","low_light","backlit","artificial_light","mixed"]
BackgroundCondition=Literal["clean","moderately_busy","busy"]
DeviceTier=Literal["entry_android","midrange_android","flagship_android","iphone","action_camera","high_speed_camera","unknown"]
@dataclass(slots=True,frozen=True)
class ReferenceMeasurement:
    metric_name:str; value:float; unit:str; source:str; uncertainty:float|None=None
    def to_dict(self): return asdict(self)
@dataclass(slots=True,frozen=True)
class ValidationClipManifest:
    clip_id:str; event:str; video_path:str; athlete_id:str|None; athlete_level:str|None; city_tier:str|None; state:str|None
    device_model:str|None; device_tier:DeviceTier; fps:float; resolution_width:int; resolution_height:int; camera_view:str
    camera_distance_m:float|None; camera_height_m:float|None; lighting:LightingCondition; background:BackgroundCondition; surface:str|None
    full_body_visible:bool; feet_visible_percent:float; occlusion_percent:float; scene_calibrated:bool
    reference_measurements:tuple[ReferenceMeasurement,...]=(); tags:tuple[str,...]=(); notes:str|None=None; schema_version:str="0.1.0"
    def to_dict(self)->dict[str,Any]:
        d=asdict(self); d["reference_measurements"]=[x.to_dict() for x in self.reference_measurements]; d["tags"]=list(self.tags); return d
def validate_manifest(m:ValidationClipManifest)->dict[str,Any]:
    issues=[]
    if m.event not in ("sprint","hurdles","long_jump","high_jump"): issues.append("Unsupported athletics event.")
    if m.fps<=0: issues.append("FPS must be positive.")
    if m.resolution_width<=0 or m.resolution_height<=0: issues.append("Resolution must be positive.")
    if not 0<=m.feet_visible_percent<=100: issues.append("feet_visible_percent must be between 0 and 100.")
    if not 0<=m.occlusion_percent<=100: issues.append("occlusion_percent must be between 0 and 100.")
    return {"valid":not issues,"issues":issues}
def build_stress_test_dimensions():
    return {"lighting":["bright_daylight","overcast","low_light","backlit","artificial_light","mixed"],"background":["clean","moderately_busy","busy"],"camera_view":["Side View","Front View","Angled View"],"fps":[25,30,60,120,240],"device_tier":["entry_android","midrange_android","flagship_android","iphone","action_camera","high_speed_camera"],"occlusion_percent_bands":["0-5","5-15","15-30","30+"],"feet_visibility_bands":["95-100","80-95","50-80","<50"]}
