from __future__ import annotations
import math
from app.services.motion.angular_kinematics import compute_angular_motion
from app.services.motion.derivatives import compute_point_motion
from app.services.motion.models import PointSample, ScalarSample, SegmentDefinition, SegmentKinematicState

def compute_segment_kinematics(*, segment: SegmentDefinition, proximal_samples: list[PointSample], distal_samples: list[PointSample], smoothing_window: int = 5) -> list[SegmentKinematicState]:
    pmap = {s.timestamp_ms:s for s in proximal_samples}
    dmap = {s.timestamp_ms:s for s in distal_samples}
    common = sorted(set(pmap) & set(dmap))
    if len(common) < 2:
        return []
    mids, angles, lengths, confs, frames = [], [], {}, {}, {}
    for t in common:
        p,d = pmap[t], dmap[t]
        conf = min(p.confidence,d.confidence)
        mx,my = (p.x+d.x)/2.0, (p.y+d.y)/2.0
        angle = math.degrees(math.atan2(d.y-p.y,d.x-p.x))
        mids.append(PointSample(p.frame_index,t,mx,my,conf))
        angles.append(ScalarSample(p.frame_index,t,angle,conf))
        lengths[t] = ((d.x-p.x)**2 + (d.y-p.y)**2)**0.5
        confs[t], frames[t] = conf, p.frame_index
    pmotion = compute_point_motion(mids,smoothing_window=smoothing_window)
    amotion = compute_angular_motion(angles,smoothing_window=smoothing_window,unwrap=True)
    amap = {s.timestamp_ms:s for s in amotion}
    return [
        SegmentKinematicState(
            segment_name=segment.name, frame_index=frames[s.timestamp_ms],
            timestamp_ms=s.timestamp_ms, midpoint_x=s.x, midpoint_y=s.y,
            length=round(lengths[s.timestamp_ms],6),
            orientation_degrees=amap[s.timestamp_ms].value,
            linear_velocity_x=s.velocity_x, linear_velocity_y=s.velocity_y,
            linear_speed=s.speed, angular_velocity_dps=amap[s.timestamp_ms].velocity,
            confidence=round(confs[s.timestamp_ms],4),
        )
        for s in pmotion if s.timestamp_ms in amap
    ]
