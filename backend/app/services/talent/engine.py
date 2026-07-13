from __future__ import annotations
from app.services.talent.benchmarking import benchmark_profile
from app.services.talent.cohorts import filter_cohort
from app.services.talent.models import AthleteProfileVector
from app.services.talent.similarity import find_similar_athletes
DEFAULT_FEATURE_WEIGHTS={"mechanical_efficiency_score":1.40,"front_side_score":1.15,"back_side_score":1.15,"ground_contact_ms":1.20,"cadence_spm":1.00,"symmetry_score":1.00,"vertical_oscillation_percent":0.90,"push_off_completion_score":1.00}

def analyze_similarity_and_benchmark(*, target: AthleteProfileVector, population: list[AthleteProfileVector], same_age_group: bool=True, same_sex: bool=True, same_level: bool=False, top_k: int=10) -> dict:
    cohort=filter_cohort(population,event=target.event,age_group=target.age_group if same_age_group else None,sex=target.sex if same_sex else None,level=target.level if same_level else None,exclude_athlete_id=target.athlete_id)
    benchmark=benchmark_profile(target,cohort)
    similarity=find_similar_athletes(target,cohort,feature_weights=DEFAULT_FEATURE_WEIGHTS,top_k=top_k)
    return {"status":"completed" if benchmark["status"]=="completed" or similarity["status"]=="completed" else "insufficient_data","target_athlete_id":target.athlete_id,"cohort_definition":{"event":target.event,"age_group":target.age_group if same_age_group else None,"sex":target.sex if same_sex else None,"level":target.level if same_level else None,"cohort_size":len(cohort)},"benchmark":benchmark,"similarity":similarity,"engine_version":"0.1.0","validation_level":"experimental"}
