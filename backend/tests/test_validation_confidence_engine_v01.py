import unittest
from app.services.validation.agreement import compare_repeated_runs
from app.services.validation.calibration import LinearCalibration, calibrate_distance
from app.services.validation.confidence import build_confidence_payload
from app.services.validation.reliability import summarize_pipeline_reliability
from app.services.validation.reporting import build_metric_estimate
from app.services.validation.uncertainty import estimate_sample_uncertainty, propagate_independent_uncertainty
from app.services.validation.versioning import build_version_registry

class TestValidationConfidenceEngineV01(unittest.TestCase):
    def test_uncertainty_estimation(self):
        r=estimate_sample_uncertainty([100.0,102.0,98.0,101.0])
        self.assertEqual(r['status'],'estimated'); self.assertGreater(r['confidence_interval_half_width'],0.0)
    def test_uncertainty_propagation(self):
        self.assertGreater(propagate_independent_uncertainty(partial_derivatives=[1.0,2.0],input_uncertainties=[0.1,0.2]),0.0)
    def test_confidence_and_reliability(self):
        p=build_confidence_payload(landmark_confidence=0.95,motion_confidence=0.90,event_confidence=0.85,physics_confidence=0.75)
        r=summarize_pipeline_reliability(pose_scores=[0.95,0.92],motion_scores=[0.90,0.88],event_scores=[0.85,0.80],physics_scores=[0.75,0.70])
        self.assertIsNotNone(p['score']); self.assertIsNotNone(r.overall_score)
    def test_repeatability(self):
        self.assertEqual(compare_repeated_runs([[100,101],[99,100],[101,102]])['status'],'completed')
    def test_calibration(self):
        c=LinearCalibration(0.5,2.0); self.assertEqual(calibrate_distance(0.25,c),1.0)
    def test_metric_tier_and_versions(self):
        m=build_metric_estimate(name='ground_contact_time',value=110.0,unit='ms',uncertainty=5.0,confidence=0.91,tier='estimated',method='multi_signal_gait_fusion',version='0.1.0')
        v=build_version_registry(); self.assertEqual(m.tier,'estimated'); self.assertIn('validation_engine',v['components'])
if __name__=='__main__': unittest.main()
