from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class EvidenceSignal:
    name: str
    value: float
    reliability: float
    weight: float
    supports_event: bool = True
    def normalized_value(self) -> float:
        return max(0.0, min(1.0, float(self.value)))
    def normalized_reliability(self) -> float:
        return max(0.0, min(1.0, float(self.reliability)))
    def contribution(self) -> float:
        if not self.supports_event: return 0.0
        return self.normalized_value()*self.normalized_reliability()*max(0.0,float(self.weight))
    def to_dict(self)->dict[str,Any]: return asdict(self)

def normalize_signal(value: float, *, minimum: float, maximum: float, invert: bool=False)->float:
    if maximum<=minimum: raise ValueError('maximum must be greater than minimum.')
    n=(float(value)-minimum)/(maximum-minimum)
    n=max(0.0,min(1.0,n))
    if invert: n=1.0-n
    return round(n,6)
