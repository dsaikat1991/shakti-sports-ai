import unittest
from app.services.validation.capabilities import create_default_capability_registry
from app.services.validation.dataset_manifest import ReferenceMeasurement,ValidationClipManifest,build_stress_test_dimensions,validate_manifest
from app.services.validation.benchmark_plan import build_validation_plan
class TestFoundation(unittest.TestCase):
    def test_blocks_valgus(self):
        r=create_default_capability_registry().evaluate("knee_valgus",event="sprint",camera_view="Side View",camera_mode="single_camera_2d",fps=60,landmark_confidence=.95,scene_calibrated=False,force_reference_available=False)
        self.assertFalse(r["available"])
    def test_allows_angle(self):
        r=create_default_capability_registry().evaluate("joint_angle_2d",event="sprint",camera_view="Side View",camera_mode="single_camera_2d",fps=30,landmark_confidence=.9,scene_calibrated=False,force_reference_available=False)
        self.assertTrue(r["available"])
    def test_manifest(self):
        m=ValidationClipManifest("clip-1","sprint","data/clip.mp4","a1","district","tier-3","West Bengal","Android","entry_android",30,1920,1080,"Side View",18,1.2,"bright_daylight","busy","synthetic_track",True,96,4,False,(ReferenceMeasurement("sprint_time",11.42,"s","electronic_timing_gate"),),("grassroots",),None)
        self.assertTrue(validate_manifest(m)["valid"])
    def test_plan(self):
        self.assertIn("entry_android",build_stress_test_dimensions()["device_tier"]); self.assertGreater(len(build_validation_plan()["targets"]),0)
if __name__=="__main__": unittest.main()
