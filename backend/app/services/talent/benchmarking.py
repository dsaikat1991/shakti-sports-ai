from __future__ import annotations
from statistics import mean
from app.services.talent.models import AthleteProfileVector, BenchmarkMetric
LOWER_IS_BETTER={"ground_contact_ms","vertical_oscillation_percent","cadence_cv_percent","contact_cv_percent","flight_cv_percent","back_side_duration_ms","trailing_distance_percent"}

def percentile_rank(*, value: float, cohort_values: list[float], lower_is_better: bool) -> float|None:
    if not cohort_values: return None
    count=sum(1 for v in cohort_values if (v>=value if lower_is_better else v<=value))
    return round(count/len(cohort_values)*100.0,2)

def benchmark_profile(target: AthleteProfileVector, cohort: list[AthleteProfileVector], *, lower_is_better_map: set[str]|None=None) -> dict:
    active=lower_is_better_map or LOWER_IS_BETTER; metrics=[]
    for name,value in target.features.items():
        vals=[p.features[name] for p in cohort if name in p.features]
        if not vals: continue
        pct=percentile_rank(value=value,cohort_values=vals,lower_is_better=name in active)
        confs=[p.confidences[name] for p in cohort if p.confidences and name in p.confidences]
        tc=target.confidences.get(name) if target.confidences else None
        if tc is not None: confs.append(tc)
        conf=round(mean(confs)*100.0,2) if confs else None
        metrics.append(BenchmarkMetric(name,float(value),pct or 0.0,len(vals),"lower_is_better" if name in active else "higher_is_better",conf))
    metrics.sort(key=lambda m:m.percentile,reverse=True)
    return {"status":"completed" if metrics else "insufficient_data","athlete_id":target.athlete_id,"event":target.event,"cohort_size":len(cohort),"metrics":[m.to_dict() for m in metrics],"top_strengths":[m.to_dict() for m in metrics if m.percentile>=80][:5],"development_areas":[m.to_dict() for m in sorted(metrics,key=lambda x:x.percentile) if m.percentile<=30][:5],"engine_version":"0.1.0"}
