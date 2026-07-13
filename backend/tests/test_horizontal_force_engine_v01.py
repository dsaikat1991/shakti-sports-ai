import unittest
from app.services.sprint.horizontal_force_engine import analyze_horizontal_force, analyze_horizontal_force_by_phase
from app.services.sprint.horizontal_force_models import HorizontalForceFrame
from app.services.sprint.horizontal_force_scoring import force_orientation_percent

def frame(index:int, *, phase:str='drive', ax:float=3.0, ay:float=1.0, trunk:float=48.0, shin:float=60.0, contact:float=145.0) -> HorizontalForceFrame:
    return HorizontalForceFrame(frame_index=index,timestamp_ms=index*40,phase=phase,side='left',com_velocity_x=4.0+index*0.2,com_velocity_y=0.2,com_acceleration_x=ax,com_acceleration_y=ay,trunk_angle_deg=trunk,shin_angle_deg=shin,ground_contact_probability=0.90,toe_off_probability=0.30,contact_time_ms=contact,confidence=0.94)

class TestHorizontalForceEngineV01(unittest.TestCase):
    def test_orientation_prefers_horizontal_acceleration(self):
        self.assertGreater(force_orientation_percent(4.0,1.0),90.0)
    def test_drive_phase_analysis(self):
        result=analyze_horizontal_force([frame(i) for i in range(6)],phase='drive')
        self.assertEqual(result['status'],'experimental')
        self.assertGreater(result['metrics']['horizontal_force_orientation_percent'],70.0)
        self.assertGreater(result['metrics']['overall_horizontal_force_score'],70.0)
        self.assertIsNotNone(result['metrics']['confidence'])
    def test_vertical_bias_reduces_score(self):
        strong=analyze_horizontal_force([frame(i,ax=4.0,ay=0.8) for i in range(6)],phase='drive')
        weak=analyze_horizontal_force([frame(i,ax=1.0,ay=4.0) for i in range(6)],phase='drive')
        self.assertGreater(strong['metrics']['overall_horizontal_force_score'],weak['metrics']['overall_horizontal_force_score'])
    def test_phase_specific_ranges(self):
        frames=[]
        for phase,trunk,shin,contact in [('drive',48.0,60.0,145.0),('transition',68.0,68.0,120.0),('maximum_velocity',84.0,76.0,98.0)]:
            frames.extend([frame(i,phase=phase,trunk=trunk,shin=shin,contact=contact) for i in range(5)])
        result=analyze_horizontal_force_by_phase(frames)
        self.assertEqual(result['status'],'completed')
        self.assertIsNotNone(result['overall_phase_average_score'])
        self.assertEqual(len(result['phases']),3)
    def test_insufficient_data(self):
        self.assertEqual(analyze_horizontal_force([frame(0),frame(1)],phase='drive')['status'],'insufficient_data')

if __name__=='__main__': unittest.main()
