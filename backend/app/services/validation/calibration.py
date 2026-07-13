from __future__ import annotations
from dataclasses import dataclass
from typing import Any
@dataclass(slots=True, frozen=True)
class LinearCalibration:
    normalized_distance: float
    real_distance_m: float
    @property
    def meters_per_normalized_unit(self)->float:
        if self.normalized_distance<=0: raise ValueError('normalized_distance must be positive.')
        return self.real_distance_m/self.normalized_distance

def calibrate_distance(normalized_value:float,calibration:LinearCalibration)->float: return round(normalized_value*calibration.meters_per_normalized_unit,6)
def calibrate_velocity(normalized_velocity:float,calibration:LinearCalibration)->float: return round(normalized_velocity*calibration.meters_per_normalized_unit,6)
def calibration_summary(calibration:LinearCalibration)->dict[str,Any]:
    return {"status":"calibrated","meters_per_normalized_unit":round(calibration.meters_per_normalized_unit,6),"reference_normalized_distance":calibration.normalized_distance,"reference_real_distance_m":calibration.real_distance_m}
