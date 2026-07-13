from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class FootTrajectoryFrame:
    frame_index:int; timestamp_ms:int; side:str; phase:str
    toe_x:float; toe_y:float; heel_x:float; heel_y:float
    ankle_x:float; ankle_y:float; knee_x:float; knee_y:float
    hip_x:float; hip_y:float; com_x:float; com_y:float
    contact_probability:float|None; toe_off_probability:float|None
    confidence:float
    def to_dict(self)->dict[str,Any]: return asdict(self)

@dataclass(slots=True, frozen=True)
class FootTrajectoryMetrics:
    side:str; phase:str; frames_used:int
    maximum_toe_clearance_normalized:float|None
    maximum_heel_recovery_height_normalized:float|None
    horizontal_recovery_range_normalized:float|None
    trajectory_path_length_normalized:float|None
    trajectory_directness_score:float|None
    recovery_timing_percent:float|None
    strike_preparation_score:float|None
    foot_loop_compactness_score:float|None
    trajectory_stability_score:float|None
    overall_foot_trajectory_score:float|None
    rating:str; confidence:float|None
    def to_dict(self)->dict[str,Any]: return asdict(self)
