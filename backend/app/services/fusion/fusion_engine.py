from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.services.fusion.bayesian import update_with_evidence_sequence
from app.services.fusion.consistency import enforce_event_consistency
from app.services.fusion.probabilities import logistic_probability
from app.services.fusion.signals import EvidenceSignal
from app.services.fusion.temporal import detect_local_peaks, smooth_probabilities
from app.services.fusion.voting import weighted_vote

@dataclass(slots=True, frozen=True)
class FusionFrame:
    side: str
    frame_index: int
    timestamp_ms: int
    event_type: str
    signals: tuple[EvidenceSignal,...]
    def to_dict(self)->dict[str,Any]:
        return {'side':self.side,'frame_index':self.frame_index,'timestamp_ms':self.timestamp_ms,'event_type':self.event_type,'signals':[s.to_dict() for s in self.signals]}

def score_fusion_frame(frame: FusionFrame, *, prior_probability: float=0.20)->dict[str,Any]:
    vote=weighted_vote(list(frame.signals),minimum_supporting_signals=2)
    vote_score=float(vote['score']); logistic=logistic_probability(vote_score,midpoint=0.55,steepness=9.0)
    evidence=[(max(0.05,s.normalized_value()*s.normalized_reliability()),max(0.05,1.0-s.normalized_value()*s.normalized_reliability())) for s in frame.signals if s.supports_event]
    posterior=update_with_evidence_sequence(prior=prior_probability,evidence=evidence) if evidence else prior_probability
    fused=vote_score*0.45+logistic*0.25+posterior*0.30
    return {'frame':frame.to_dict(),'vote':vote,'posterior_probability':round(posterior,6),'fused_probability':round(max(0.0,min(1.0,fused)),6)}

def detect_fused_events(frames: list[FusionFrame], *, event_threshold: float=0.70, smoothing_window: int=5, minimum_gap_ms: int=60)->dict[str,Any]:
    if not frames: return {'status':'insufficient_data','events':[]}
    grouped={}
    for f in frames: grouped.setdefault((f.side,f.event_type),[]).append(f)
    candidates=[]; debug={}
    for (side,event_type),group in grouped.items():
        ordered=sorted(group,key=lambda x:x.timestamp_ms)
        scored=[score_fusion_frame(f) for f in ordered]
        probs=[x['fused_probability'] for x in scored]
        smoothed=smooth_probabilities(probs,window_size=smoothing_window)
        timestamps=[f.timestamp_ms for f in ordered]
        peaks=detect_local_peaks(smoothed,timestamps,threshold=event_threshold,radius=2,minimum_gap_ms=minimum_gap_ms)
        debug[f'{side}:{event_type}']={'scores':scored,'smoothed_probabilities':smoothed,'peaks':peaks}
        for peak in peaks:
            f=ordered[int(peak['index'])]
            candidates.append({'side':side,'event_type':event_type,'frame_index':f.frame_index,'timestamp_ms':f.timestamp_ms,'probability':peak['probability'],'source':'fusion_engine_v0.1'})
    consistency=enforce_event_consistency(candidates,minimum_gap_ms=minimum_gap_ms)
    return {'status':consistency['status'],'events':consistency['accepted'],'rejected_events':consistency['rejected'],'debug':debug,'method':'weighted_vote_bayesian_temporal_consistency_v0.1','limitations':['Probabilities are not statistically calibrated yet.','Thresholds require tuning against labelled athletics footage.','Event accuracy depends on pose and motion reliability.']}
