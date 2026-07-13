import unittest
from app.services.biomechanics.reliability_gate import reliability_gate, combine_landmark_gates

class TestGate(unittest.TestCase):
    def test_accept(self):
        self.assertEqual(reliability_gate({"average_score":85.0,"coverage_above_moderate_percent":90.0})["decision"], "accept")
    def test_combined_reject(self):
        self.assertEqual(combine_landmark_gates([{"decision":"accept"},{"decision":"reject"}])["decision"], "reject")

if __name__ == "__main__":
    unittest.main()
