import unittest
from app.services.sprint.foot_trajectory_engine import analyze_foot_trajectory,analyze_foot_trajectory_by_phase
from app.services.sprint.foot_trajectory_models import FootTrajectoryFrame
from app.services.sprint.foot_trajectory_report import build_foot_trajectory_report

def make_frame(index,side='left',phase='maximum_velocity',toe_x=None,toe_y=None,heel_y=None):
    toe_x=0.20+index*0.08 if toe_x is None else toe_x
    toe_y=(0.80-0.08*index if index<=3 else 0.56+0.06*(index-3)) if toe_y is None else toe_y
    heel_y=toe_y-0.05 if heel_y is None else heel_y
    return FootTrajectoryFrame(index,index*40,side,phase,toe_x,toe_y,toe_x-0.04,heel_y,toe_x-0.03,toe_y-0.06,0.45,0.50,0.50,0.42,0.50,0.46,0.85 if index in (0,7) else 0.10,0.90 if index==1 else 0.10,0.94)

class TestFootTrajectoryEngineV01(unittest.TestCase):
    def test_metrics(self):
        r=analyze_foot_trajectory([make_frame(i) for i in range(8)],side='left',phase='maximum_velocity')
        self.assertEqual(r['status'],'experimental');self.assertGreater(r['metrics']['trajectory_path_length_normalized'],0);self.assertIsNotNone(r['metrics']['overall_foot_trajectory_score'])
    def test_irregular_reduces_directness(self):
        smooth=analyze_foot_trajectory([make_frame(i) for i in range(8)],side='left',phase='maximum_velocity')
        irregular=analyze_foot_trajectory([make_frame(i,toe_x=0.20+i*0.08+(0.18 if i%2==0 else -0.18)) for i in range(8)],side='left',phase='maximum_velocity')
        self.assertGreater(smooth['metrics']['trajectory_directness_score'],irregular['metrics']['trajectory_directness_score'])
    def test_minimum(self):
        self.assertEqual(analyze_foot_trajectory([make_frame(i) for i in range(4)],side='left',phase='drive')['status'],'insufficient_data')
    def test_integration(self):
        frames=[]
        for side in ('left','right'):
            for phase in ('drive','transition','maximum_velocity'):
                frames.extend([make_frame(i,side=side,phase=phase) for i in range(8)])
        r=analyze_foot_trajectory_by_phase(frames);self.assertEqual(r['status'],'completed');self.assertIsNotNone(r['overall_average_foot_trajectory_score'])
    def test_report(self):
        r=analyze_foot_trajectory([make_frame(i) for i in range(8)],side='left',phase='maximum_velocity')
        self.assertEqual(build_foot_trajectory_report(r)['status'],'completed')
if __name__=='__main__':unittest.main()
