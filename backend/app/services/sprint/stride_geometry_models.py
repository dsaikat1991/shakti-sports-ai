from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class FootContactEvent:
    """
    A single detected ground-contact event, with the spatial landmark
    positions needed for stride-geometry analysis attached (built by
    `pose_remote/stride_velocity_bridge.py::build_foot_contact_events`).

    **Coordinate system, audited and documented 2026-07-17 (§stride-
    geometry correction pass)** - this was previously undocumented on
    this dataclass, a real gap: every `_x`/`_y` field is a **normalized
    2D image-space coordinate** (0.0-1.0 range, origin top-left, Y
    increases downward - the same convention as the underlying pose
    landmarks), captured from a **side-view camera** (the live quality
    gate requires `camera_view.classification == "Side View"` before any
    biomechanics analysis runs at all, this module included).

    Given a side-view camera, only two real-world axes are actually
    observable in this coordinate system:
    - **X (image-horizontal) is a genuine, meaningful proxy for
      along-track distance** - how far the athlete has travelled in the
      direction of running - because a side-on camera's horizontal axis
      is (approximately) parallel to the direction of travel.
    - **Y (image-vertical) is a genuine, meaningful proxy for height off
      the ground** - foot height during swing/stance, vertical centre-of-
      mass oscillation.
    - **The true mediolateral (left-right, mediolateral/lateral) axis -
      the dimension a real "crossover gait" or "step width" measurement
      requires - is oriented almost exactly ALONG the camera's line of
      sight in a side-view shot, and is therefore not directly observable
      in this 2D projection at all.** Any metric computed by comparing X
      or Y between two contacts and calling the result "width" or
      "crossover" is measuring *something* - but not the biomechanical
      quantity that name implies. See `stride_geometry_engine.py`'s
      module docstring for how this is now handled.

    `leg_split` (set by `build_foot_contact_events`) is the horizontal
    (X) distance between this contact's foot and the *opposite* foot
    within the *same frame* - camera-motion-invariant by construction
    (§9 bug #6 of docs/ENGINEERING_HANDOFF.md), but NOT camera-*angle*-
    invariant: an oblique (non-pure-side-on) camera introduces
    perspective distortion where the near-camera leg's apparent
    horizontal motion is exaggerated relative to the far leg's - a
    distinct failure mode from the motion-artifact this field was
    designed to fix. See the left/right asymmetry finding in the
    stride-geometry correction pass's audit report for a concrete,
    measured example (0.395 vs. 1.367 - a 3.46x difference - from the
    same athlete, same clip).

    `confidence` is on a **0-100 scale** (sourced from
    `biomechanics/contact_events.py::ContactEvent.confidence`, itself a
    peak-detection-prominence score, not a ground-truth-verified
    accuracy measure - the underlying detector is confirmed unreliable
    for some camera angles, §10/§11 of docs/ENGINEERING_HANDOFF.md).
    Callers must normalize to [0, 1] before passing this into anything
    built on `clamp()`'s default range - see
    `stride_geometry_scoring.py::normalize_0_100_to_unit`.
    """

    side: str
    frame_index: int
    timestamp_ms: int

    foot_x: float
    foot_y: float
    com_x: float
    com_y: float

    toe_x: float | None
    toe_y: float | None
    heel_x: float | None
    heel_y: float | None

    confidence: float

    leg_split: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class StrideGeometryContext:
    body_height_normalized: float | None = None
    leg_length_normalized: float | None = None
    real_world_scale_m_per_unit: float | None = None
    athlete_height_m: float | None = None


# A fixed, always-populated explanation for why the lateral-plane metrics
# below are None rather than a computed value - see FootContactEvent's
# coordinate-system docstring and stride_geometry_engine.py's module
# docstring for the full reasoning. Exposed as a constant so the reason
# is co-located with the fields it explains and can't drift out of sync.
LATERAL_METRICS_UNAVAILABLE_REASON = (
    "Not computable from a single side-view 2D camera. True mediolateral "
    "(left-right) separation - what 'crossover' and 'step width' both "
    "require - is oriented along this camera's line of sight and is not "
    "observable in this projection. A prior version of this module "
    "approximated these by comparing image-vertical (Y) position instead, "
    "which measures foot-height difference, not lateral separation, and "
    "produced implausible values on real footage (a confirmed axis-"
    "selection bug, corrected 2026-07-17 - see docs/ENGINEERING_HANDOFF.md). "
    "Reliably measuring this would require a front/rear-view camera pass, "
    "stereo or 3D pose estimation, or a calibrated ground-plane homography "
    "- none of which this pipeline has today."
)


@dataclass(slots=True, frozen=True)
class StrideGeometryMetrics:
    contacts_used: int
    left_contacts_used: int
    right_contacts_used: int

    left_step_length_normalized: float | None
    right_step_length_normalized: float | None
    average_step_length_normalized: float | None
    average_stride_length_normalized: float | None

    average_step_length_m: float | None
    average_stride_length_m: float | None

    normalized_step_length_leg_ratio: float | None
    expected_optimal_step_length_normalized: float | None
    optimal_step_length_difference_percent: float | None

    # Both None as of the §stride-geometry correction pass - not
    # computable from a side-view 2D camera. See
    # LATERAL_METRICS_UNAVAILABLE_REASON. Kept as named fields (rather
    # than removed) so a future consumer sees an explicit, explained
    # absence instead of a missing key.
    average_step_width_normalized: float | None
    average_step_width_m: float | None
    lateral_metrics_unavailable_reason: str | None

    average_foot_offset_from_com_percent_body_height: float | None

    # None as of the §stride-geometry correction pass, same reason as
    # step width above - "crossover" is a lateral-plane phenomenon this
    # camera setup cannot observe.
    crossover_contacts: int | None
    crossover_rate_percent: float | None

    toe_in_contacts: int
    neutral_toe_contacts: int
    toe_out_contacts: int

    step_length_symmetry_score: float | None
    geometry_stability_score: float | None
    overall_stride_geometry_score: float | None

    rating: str
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
