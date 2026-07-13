from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
@dataclass(slots=True,frozen=True)
class ValidationTarget:
    metric_name:str; reference_system:str; primary_error_metric:str; secondary_metrics:tuple[str,...]; minimum_sample_size:int; acceptance_target:str; version:str="0.1.0"
    def to_dict(self):
        d=asdict(self); d["secondary_metrics"]=list(self.secondary_metrics); return d
TARGETS=(
ValidationTarget("sprint_time","electronic_timing_gates","mean_absolute_error_ms",("bias_ms","limits_of_agreement","icc"),50,"< 20 ms"),
ValidationTarget("cadence","manual_high_speed_video","mean_absolute_error_spm",("icc","coefficient_of_variation"),50,"< 2 steps/min"),
ValidationTarget("ground_contact_time","force_plate_or_instrumented_treadmill","mean_absolute_error_ms",("bias_ms","limits_of_agreement","icc"),100,"< 10 ms"),
ValidationTarget("flight_time","force_plate_or_high_speed_video","mean_absolute_error_ms",("bias_ms","limits_of_agreement"),100,"< 10 ms"),
ValidationTarget("joint_angle_2d","manual_digitization_or_marker_based_motion_capture","mean_absolute_error_degrees",("rmse_degrees","icc"),100,"< 5 degrees"))
def build_validation_plan()->dict[str,Any]:
    return {"status":"planned","targets":[t.to_dict() for t in TARGETS],"required_reporting":["sample_size","mean_absolute_error","bias","limits_of_agreement","intraclass_correlation","confidence_intervals","failure_rate","results_by_recording_condition"]}
