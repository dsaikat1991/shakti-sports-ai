from __future__ import annotations
from typing import Any
ALLOWED_TRANSITIONS={'flight':('initial_contact',),'stance':('toe_off',)}

def enforce_event_consistency(candidates: list[dict[str,Any]], *, minimum_gap_ms: int=60)->dict[str,Any]:
    ordered=sorted(candidates,key=lambda x:int(x['timestamp_ms']))
    state={'left':'flight','right':'flight'}; last={'left':-10000,'right':-10000}; accepted=[]; rejected=[]
    for c in ordered:
        side=str(c['side']); et=str(c['event_type']); t=int(c['timestamp_ms']); current=state[side]
        if et not in ALLOWED_TRANSITIONS[current]:
            rejected.append({**c,'reason':f'invalid_transition_from_{current}'}); continue
        if t-last[side]<minimum_gap_ms:
            rejected.append({**c,'reason':'minimum_gap_violation'}); continue
        accepted.append(c); state[side]='stance' if et=='initial_contact' else 'flight'; last[side]=t
    return {'status':'completed' if accepted else 'insufficient_data','accepted':accepted,'rejected':rejected,'final_state':state}
