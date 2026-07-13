import unittest
from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.landmark_reliability import evaluate_landmark_reliability, summarize_landmark_reliability

def landmark(x, y, visibility=1.0, presence=1.0):
    return {"x": x, "y": y, "visibility": visibility, "presence": presence}

def frame(index, x, y, visibility=1.0):
    points = [landmark(0.5, 0.5) for _ in range(33)]
    points[27] = landmark(x, y, visibility, visibility)
    return FrameMetrics(index, index * 33, {}, None, {}, tuple(points))

class TestReliability(unittest.TestCase):
    def test_smooth_visible_scores_high(self):
        items = evaluate_landmark_reliability([frame(i, 0.4 + i * 0.01, 0.7) for i in range(6)], 27)
        self.assertGreater(summarize_landmark_reliability(items)["average_score"], 75.0)
    def test_low_visibility_scores_lower(self):
        items = evaluate_landmark_reliability([frame(i, 0.4 + i * 0.01, 0.7, 0.2) for i in range(6)], 27)
        self.assertLess(summarize_landmark_reliability(items)["average_score"], 60.0)
    def test_jump_penalised(self):
        items = evaluate_landmark_reliability([frame(0,0.4,0.7), frame(1,0.41,0.7), frame(2,0.8,0.2), frame(3,0.43,0.7), frame(4,0.44,0.7)], 27)
        self.assertLess(items[2].motion_consistency_score, 0.25)

if __name__ == "__main__":
    unittest.main()
