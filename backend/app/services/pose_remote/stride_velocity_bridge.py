from __future__ import annotations

from typing import Any

from app.services.biomechanics.centre_of_mass import extract_centre_series
from app.services.biomechanics.contact_events import (
    LEFT_ANKLE,
    LEFT_FOOT_INDEX,
    LEFT_HEEL,
    RIGHT_ANKLE,
    RIGHT_FOOT_INDEX,
    RIGHT_HEEL,
)
from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.pose.landmark_usability import landmark_is_usable
from app.services.sprint.stride_geometry_models import FootContactEvent

_SIDE_INDICES: dict[str, dict[str, int]] = {
    "left": {"ankle": LEFT_ANKLE, "heel": LEFT_HEEL, "toe": LEFT_FOOT_INDEX},
    "right": {"ankle": RIGHT_ANKLE, "heel": RIGHT_HEEL, "toe": RIGHT_FOOT_INDEX},
}


def _read_coordinate(landmark: Any, name: str) -> float:
    if isinstance(landmark, dict):
        return float(landmark.get(name, 0.0))

    return float(getattr(landmark, name, 0.0))


def _landmark_xy(
    landmarks: tuple[Any, ...],
    index: int,
    *,
    backend: str,
) -> tuple[float, float] | None:
    if index >= len(landmarks):
        return None

    landmark = landmarks[index]

    if not landmark_is_usable(landmark, backend=backend):
        return None

    return (
        _read_coordinate(landmark, "x"),
        _read_coordinate(landmark, "y"),
    )


def build_foot_contact_events(
    contact_events: dict[str, list[dict[str, Any]]],
    frame_metrics: list[FrameMetrics],
) -> list[FootContactEvent]:
    """
    Attach spatial landmark positions to detected ground-contact events.

    ``detect_contact_events`` only tracks foot *height* (for timing);
    this bridge looks the contact's frame back up in ``frame_metrics``
    to attach the ankle/heel/toe/centre-of-mass positions that
    ``analyze_stride_geometry`` needs, without changing the
    already-validated contact detector. ``leg_split`` is the horizontal
    distance between this contact's foot and the *opposite* foot within
    the *same frame* - unlike foot_x on its own, this is unaffected by
    camera panning/tracking between frames.
    """
    frames_by_index = {frame.frame_index: frame for frame in frame_metrics}
    centre_by_index = {
        sample.frame_index: sample
        for sample in extract_centre_series(frame_metrics)
    }
    opposite_side = {"left": "right", "right": "left"}

    results: list[FootContactEvent] = []

    for side, indices in _SIDE_INDICES.items():
        opposite_indices = _SIDE_INDICES[opposite_side[side]]

        for event in contact_events.get(side, []):
            frame_index = event.get("peak_frame_index")
            frame = frames_by_index.get(frame_index)
            centre = centre_by_index.get(frame_index)

            if frame is None or centre is None:
                continue

            backend = getattr(frame, "backend", "mediapipe")
            ankle_xy = _landmark_xy(
                frame.landmarks, indices["ankle"], backend=backend
            )

            if ankle_xy is None:
                continue

            heel_xy = _landmark_xy(
                frame.landmarks, indices["heel"], backend=backend
            )
            toe_xy = _landmark_xy(
                frame.landmarks, indices["toe"], backend=backend
            )
            opposite_ankle_xy = _landmark_xy(
                frame.landmarks, opposite_indices["ankle"], backend=backend
            )

            results.append(
                FootContactEvent(
                    side=side,
                    frame_index=frame_index,
                    timestamp_ms=int(event.get("peak_timestamp_ms", 0)),
                    foot_x=ankle_xy[0],
                    foot_y=ankle_xy[1],
                    com_x=centre.x,
                    com_y=centre.y,
                    heel_x=heel_xy[0] if heel_xy else None,
                    heel_y=heel_xy[1] if heel_xy else None,
                    toe_x=toe_xy[0] if toe_xy else None,
                    toe_y=toe_xy[1] if toe_xy else None,
                    confidence=float(event.get("confidence", 0.0)),
                    leg_split=(
                        abs(ankle_xy[0] - opposite_ankle_xy[0])
                        if opposite_ankle_xy is not None
                        else None
                    ),
                )
            )

    results.sort(key=lambda contact: (contact.timestamp_ms, contact.frame_index))
    return results


def build_stride_based_progression(
    contacts: list[FootContactEvent],
    *,
    side: str = "right",
) -> tuple[list[int], list[float]]:
    """
    Build a camera-motion-robust "distance covered" signal for sprint
    phase detection, in place of raw on-screen horizontal position.

    Raw frame position, and even the fore-aft distance between two
    *different-time* footstrikes, only reflects real running speed when
    the athlete moves in a straight line across a fixed, side-on
    camera: both collapse toward zero net progression for drills,
    loops, or any panning/tracking camera, even while the athlete keeps
    running at a steady pace. ``leg_split`` instead measures both feet
    within a *single* frame at each contact, so it is unaffected by
    camera motion between frames. Cumulatively summing it produces a
    monotonically increasing "distance covered" proxy whose derivative
    (computed by the existing ``detect_sprint_phases`` velocity logic)
    tracks real stride amplitude over time.

    Only one side is used: contact timing between the two feet is not
    perfectly symmetric (occlusion/detection noise differs per side),
    and mixing both would alternate between each side's split, creating
    artificial zig-zag "acceleration" from the alternation itself
    rather than genuine pace changes.
    """
    ordered = sorted(
        (
            contact
            for contact in contacts
            if contact.side == side and contact.leg_split is not None
        ),
        key=lambda contact: (contact.timestamp_ms, contact.frame_index),
    )

    timestamps_ms: list[int] = []
    cumulative_distance: list[float] = []
    running_total = 0.0

    for contact in ordered:
        running_total += contact.leg_split
        timestamps_ms.append(contact.timestamp_ms)
        cumulative_distance.append(running_total)

    return timestamps_ms, cumulative_distance
