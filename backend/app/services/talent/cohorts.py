from __future__ import annotations
from app.services.talent.models import AthleteProfileVector

def filter_cohort(profiles: list[AthleteProfileVector], *, event: str|None=None, age_group: str|None=None, sex: str|None=None, level: str|None=None, exclude_athlete_id: str|None=None) -> list[AthleteProfileVector]:
    result=profiles
    if event is not None: result=[p for p in result if p.event==event]
    if age_group is not None: result=[p for p in result if p.age_group==age_group]
    if sex is not None: result=[p for p in result if p.sex==sex]
    if level is not None: result=[p for p in result if p.level==level]
    if exclude_athlete_id is not None: result=[p for p in result if p.athlete_id!=exclude_athlete_id]
    return result
