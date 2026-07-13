from __future__ import annotations
from typing import Any
from app.services.fusion.signals import EvidenceSignal

def weighted_vote(signals: list[EvidenceSignal], *, minimum_supporting_signals: int=2)->dict[str,Any]:
    supporting=[s for s in signals if s.supports_event and s.weight>0.0 and s.reliability>0.0]
    if len(supporting)<minimum_supporting_signals:
        return {'status':'insufficient_support','score':0.0,'support_count':len(supporting),'supporting_signals':[s.name for s in supporting]}
    numerator=sum(s.contribution() for s in supporting)
    denominator=sum(max(0.0,s.weight) for s in supporting)
    score=numerator/denominator if denominator>0 else 0.0
    return {'status':'completed','score':round(max(0.0,min(1.0,score)),6),'support_count':len(supporting),'supporting_signals':[s.name for s in supporting]}
