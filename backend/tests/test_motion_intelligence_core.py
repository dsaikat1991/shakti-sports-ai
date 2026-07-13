import unittest
from app.services.motion.models import ScalarSample, PointSample, SegmentDefinition
from app.services.motion.derivatives import compute_scalar_motion, compute_point_motion
from app.services.motion.angular_kinematics import compute_angular_motion, unwrap_degrees
from app.services.motion.segment_kinematics import compute_segment_kinematics

class TestMotionIntelligenceCore(unittest.TestCase):
    def test_scalar_velocity(self):
        samples=[ScalarSample(i,i*100,i*0.5) for i in range(8)]
        states=compute_scalar_motion(samples,smoothing_window=1)
        self.assertAlmostEqual(states[3].velocity,5.0,places=6)

    def test_point_motion(self):
        samples=[PointSample(i,i*100,i*0.1,i*0.2) for i in range(8)]
        states=compute_point_motion(samples,smoothing_window=1)
        self.assertGreater(states[3].speed,0.0)

    def test_duplicate_timestamps_raise(self):
        with self.assertRaises(ValueError):
            compute_scalar_motion([
                ScalarSample(0,0,0.0),
                ScalarSample(1,0,1.0),
            ])

    def test_angle_unwrap_and_velocity(self):
        self.assertGreater(unwrap_degrees([170,179,-178])[2],179)
        samples=[ScalarSample(i,i*100,i*10.0) for i in range(6)]
        states=compute_angular_motion(samples,smoothing_window=1)
        self.assertAlmostEqual(states[3].velocity,100.0,places=4)

    def test_segment_kinematics(self):
        proximal=[PointSample(i,i*100,i*0.1,0.0) for i in range(6)]
        distal=[PointSample(i,i*100,i*0.1+1.0,0.0) for i in range(6)]
        states=compute_segment_kinematics(
            segment=SegmentDefinition("left_thigh","left_hip","left_knee"),
            proximal_samples=proximal, distal_samples=distal, smoothing_window=1,
        )
        self.assertEqual(len(states),6)
        self.assertAlmostEqual(states[2].length,1.0,places=6)
        self.assertAlmostEqual(states[2].orientation_degrees,0.0,places=6)
        self.assertGreater(states[2].linear_speed,0.0)

if __name__ == "__main__":
    unittest.main()
