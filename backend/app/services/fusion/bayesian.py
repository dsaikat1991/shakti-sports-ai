from __future__ import annotations

def update_probability(*, prior: float, likelihood_if_event: float, likelihood_if_not_event: float)->float:
    p=max(1e-6,min(1.0-1e-6,float(prior)))
    le=max(1e-6,min(1.0,float(likelihood_if_event)))
    ln=max(1e-6,min(1.0,float(likelihood_if_not_event)))
    num=le*p; den=num+ln*(1.0-p)
    return round(num/den if den>0 else p,6)

def update_with_evidence_sequence(*, prior: float, evidence: list[tuple[float,float]])->float:
    posterior=prior
    for le,ln in evidence: posterior=update_probability(prior=posterior,likelihood_if_event=le,likelihood_if_not_event=ln)
    return posterior
