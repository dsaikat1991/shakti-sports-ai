import unittest

from app.services.sprint.arm_mechanics import (
    ArmFrame,
    analyze_arm_mechanics,
)
from app.services.sprint.max_velocity_maintenance import (
    VelocityFrame,
    analyze_max_velocity_maintenance,
)
from app.services.sprint.pelvis_trunk import (
    PelvisTrunkFrame,
    analyze_pelvis_trunk,
)
from app.services.sprint.sprint_economy import (
    analyze_sprint_economy,
)
from app.services.sprint.sprint_intelligence_fusion import (
    fuse_sprint_intelligence,
)


class TestSprintIntelligenceProBundleV01(unittest.TestCase):
    def test_sprint_economy(self):
        result = analyze_sprint_economy({
            "horizontal_force_score": 88.0,
            "net_propulsion_score": 86.0,
            "braking_index": 14.0,
            "vertical_oscillation_percent": 6.5,
            "leg_spring_score": 84.0,
            "bounce_efficiency_score": 87.0,
            "cadence_cv_percent": 3.0,
            "contact_cv_percent": 4.0,
            "stride_geometry_stability_score": 90.0,
            "stride_geometry_score": 89.0,
            "foot_trajectory_score": 85.0,
            "confidences": [0.92, 0.90],
        })
        self.assertEqual(result["status"], "experimental")
        self.assertGreater(result["score"], 75.0)

    def test_arm_mechanics(self):
        frames = []
        for side in ("left", "right"):
            for i in range(6):
                frames.append(ArmFrame(
                    frame_index=i,
                    timestamp_ms=i * 40,
                    side=side,
                    phase="maximum_velocity",
                    shoulder_x=0.50,
                    shoulder_y=0.30,
                    elbow_x=0.45,
                    elbow_y=0.45,
                    wrist_x=0.42,
                    wrist_y=0.58,
                    elbow_angle_deg=95.0,
                    wrist_velocity_x=1.5 + i * 0.05,
                    wrist_velocity_y=0.6,
                    confidence=0.94,
                ))
        result = analyze_arm_mechanics(frames, phase="maximum_velocity")
        self.assertEqual(result["status"], "experimental")
        self.assertIsNotNone(result["score"])

    def test_pelvis_trunk(self):
        frames = [
            PelvisTrunkFrame(
                frame_index=i,
                timestamp_ms=i * 40,
                phase="maximum_velocity",
                left_shoulder_y=0.30 + i * 0.001,
                right_shoulder_y=0.31,
                left_hip_y=0.50,
                right_hip_y=0.505,
                shoulder_width=0.18,
                hip_width=0.14,
                trunk_angle_deg=84.0 + i * 0.2,
                head_x=0.50 + i * 0.001,
                head_y=0.18,
                com_x=0.50,
                com_y=0.48,
                confidence=0.93,
            )
            for i in range(7)
        ]
        result = analyze_pelvis_trunk(frames, phase="maximum_velocity")
        self.assertEqual(result["status"], "experimental")
        self.assertIsNotNone(result["score"])

    def test_max_velocity_maintenance(self):
        velocities = [9.8, 10.0, 10.1, 10.05, 10.0, 9.95, 9.9]
        frames = [
            VelocityFrame(
                frame_index=i,
                timestamp_ms=i * 400,
                phase="maximum_velocity",
                velocity_x=v,
                cadence_spm=286.0,
                ground_contact_ms=98.0,
                confidence=0.94,
            )
            for i, v in enumerate(velocities)
        ]
        result = analyze_max_velocity_maintenance(frames)
        self.assertEqual(result["status"], "experimental")
        self.assertGreater(result["score"], 70.0)

    def test_fusion(self):
        result = fuse_sprint_intelligence({
            "horizontal_force": {"score": 88.0, "confidence": 92.0},
            "propulsion_braking": {"score": 86.0, "confidence": 90.0},
            "stride_geometry": {"score": 84.0, "confidence": 89.0},
            "foot_trajectory": {"score": 82.0, "confidence": 88.0},
            "leg_spring": {"score": 85.0, "confidence": 90.0},
            "sprint_economy": {"score": 87.0, "confidence": 91.0},
            "arm_mechanics": {"score": 80.0, "confidence": 87.0},
            "pelvis_trunk": {"score": 83.0, "confidence": 89.0},
            "max_velocity_maintenance": {"score": 90.0, "confidence": 93.0},
        })
        self.assertEqual(result["status"], "experimental")
        self.assertGreater(result["score"], 80.0)
        self.assertEqual(result["metrics"]["engines_available"], 9)


if __name__ == "__main__":
    unittest.main()
