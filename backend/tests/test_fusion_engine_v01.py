import unittest
from app.services.fusion.bayesian import update_probability
from app.services.fusion.consistency import enforce_event_consistency
from app.services.fusion.fusion_engine import FusionFrame, detect_fused_events, score_fusion_frame
from app.services.fusion.signals import EvidenceSignal, normalize_signal
from app.services.fusion.temporal import smooth_probabilities
from app.services.fusion.voting import weighted_vote

class TestFusionEngineV01(unittest.TestCase):
    def test_signal_normalization(self):
        self.assertEqual(normalize_signal(5.0,minimum=0.0,maximum=10.0),0.5)
    def test_weighted_vote(self):
        r=weighted_vote([EvidenceSignal('a',0.9,0.95,1.0),EvidenceSignal('b',0.8,0.9,1.0)])
        self.assertEqual(r['status'],'completed'); self.assertGreater(r['score'],0.7)
    def test_bayesian_update(self):
        self.assertGreater(update_probability(prior=0.2,likelihood_if_event=0.9,likelihood_if_not_event=0.2),0.2)
    def test_temporal_smoothing(self):
        self.assertEqual(len(smooth_probabilities([0.1,0.9,0.1],window_size=3)),3)
    def test_invalid_sequence_is_rejected(self):
        r=enforce_event_consistency([{'side':'left','event_type':'toe_off','timestamp_ms':1000}])
        self.assertEqual(len(r['accepted']),0)
    def test_frame_scoring(self):
        f=FusionFrame('left',30,1000,'initial_contact',(EvidenceSignal('a',0.95,0.95,1.0),EvidenceSignal('b',0.9,0.9,1.0),EvidenceSignal('c',0.85,0.9,0.8)))
        self.assertGreater(score_fusion_frame(f)['fused_probability'],0.5)
    def test_detects_consistent_contact_and_toe_off(self):
        frames=[]
        for i in range(12):
            t=i*40; cs=0.95 if i==4 else 0.15; ts=0.95 if i==8 else 0.15
            frames.append(FusionFrame('left',i,t,'initial_contact',(EvidenceSignal('ca',cs,0.95,1.0),EvidenceSignal('cb',cs,0.95,1.0))))
            frames.append(FusionFrame('left',i,t,'toe_off',(EvidenceSignal('ta',ts,0.95,1.0),EvidenceSignal('tb',ts,0.95,1.0))))
        r=detect_fused_events(frames,event_threshold=0.35,smoothing_window=1,minimum_gap_ms=80)
        types=[e['event_type'] for e in r['events']]
        self.assertIn('initial_contact',types); self.assertIn('toe_off',types)

if __name__=='__main__': unittest.main()
