from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

EXPECTED_LANDMARK_COUNTS: dict[str, int] = {
    "halpe26": 26,
    "halpe_26": 26,
    "coco17": 17,
    "coco": 17,
    "coco_17": 17,
}

DEFAULT_EXPECTED_LANDMARKS = 26


@dataclass(slots=True, frozen=True)
class SelectionWeights:
    bounding_box_area: float = 0.40
    centre_proximity: float = 0.25
    pose_confidence: float = 0.20
    landmark_completeness: float = 0.15

    def total(self) -> float:
        return (
            self.bounding_box_area
            + self.centre_proximity
            + self.pose_confidence
            + self.landmark_completeness
        )


@dataclass(slots=True, frozen=True)
class TrackerWeights:
    bounding_box_overlap: float = 0.35
    centre_motion: float = 0.25
    size_similarity: float = 0.15
    landmark_similarity: float = 0.15
    track_id_match: float = 0.10

    def total(self) -> float:
        return (
            self.bounding_box_overlap
            + self.centre_motion
            + self.size_similarity
            + self.landmark_similarity
            + self.track_id_match
        )


# Reasons backed by a detection in the current frame. "coasting" repeats
# the last confirmed pose and must not be fed to biomechanics engines as a
# fresh sample: it would duplicate coordinates and fake zero motion.
OBSERVED_REASONS = frozenset({"selected", "tracked", "reselected"})


@dataclass(slots=True, frozen=True)
class SelectionResult:
    instance: dict[str, Any] | None
    score: float
    reason: str
    selected_index: int | None = None
    components: dict[str, float] | None = None
    candidate_scores: tuple[float, ...] = ()
    candidate_components: tuple[dict[str, float], ...] = ()


@dataclass(slots=True, frozen=True)
class TrackedSelection:
    instance: dict[str, Any] | None
    score: float
    reason: str
    frame_index: int
    components: dict[str, float] | None = None

    @property
    def is_observed(self) -> bool:
        return self.reason in OBSERVED_REASONS


def bbox_area(bbox: list[float] | None) -> float:
    if bbox is None or len(bbox) < 4:
        return 0.0
    width = max(float(bbox[2]) - float(bbox[0]), 0.0)
    height = max(float(bbox[3]) - float(bbox[1]), 0.0)
    return width * height


def bbox_centre(bbox: list[float]) -> tuple[float, float]:
    return (
        (float(bbox[0]) + float(bbox[2])) / 2.0,
        (float(bbox[1]) + float(bbox[3])) / 2.0,
    )


def bbox_iou(first: list[float] | None, second: list[float] | None) -> float:
    if first is None or second is None:
        return 0.0
    left = max(float(first[0]), float(second[0]))
    top = max(float(first[1]), float(second[1]))
    right = min(float(first[2]), float(second[2]))
    bottom = min(float(first[3]), float(second[3]))
    if right <= left or bottom <= top:
        return 0.0
    intersection = (right - left) * (bottom - top)
    union = bbox_area(first) + bbox_area(second) - intersection
    if union <= 0.0:
        return 0.0
    return intersection / union


def instance_keypoints(instance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    # Worker responses use "keypoints"; to_shakti_landmarks renames the
    # same mapping to "landmarks".
    keypoints = instance.get("keypoints")
    if keypoints is None:
        keypoints = instance.get("landmarks")
    return keypoints or {}


def expected_landmark_count(instance: dict[str, Any]) -> int:
    schema = str(instance.get("source_schema") or "").lower()
    return EXPECTED_LANDMARK_COUNTS.get(schema, DEFAULT_EXPECTED_LANDMARKS)


def selection_components(
    instance: dict[str, Any],
    *,
    width: int,
    height: int,
    weights: SelectionWeights,
) -> dict[str, float]:
    frame_area = float(max(width, 1) * max(height, 1))
    bbox = instance.get("bounding_box")

    area_score = min(bbox_area(bbox) / frame_area, 1.0)

    centre_score = 0.0
    if bbox is not None and len(bbox) >= 4:
        centre_x, centre_y = bbox_centre(bbox)
        half_diagonal = math.hypot(width / 2.0, height / 2.0)
        distance = math.hypot(
            centre_x - width / 2.0,
            centre_y - height / 2.0,
        )
        if half_diagonal > 0.0:
            centre_score = max(1.0 - distance / half_diagonal, 0.0)

    confidence_score = min(max(float(instance.get("confidence", 0.0)), 0.0), 1.0)

    keypoints = instance_keypoints(instance)
    completeness = min(
        len(keypoints) / expected_landmark_count(instance), 1.0
    )

    total = weights.total()
    final = 0.0
    if total > 0.0:
        final = (
            weights.bounding_box_area * area_score
            + weights.centre_proximity * centre_score
            + weights.pose_confidence * confidence_score
            + weights.landmark_completeness * completeness
        ) / total

    return {
        "bbox_area_score": area_score,
        "centre_score": centre_score,
        "confidence_score": confidence_score,
        "completeness_score": completeness,
        "final_score": final,
    }


def selection_score(
    instance: dict[str, Any],
    *,
    width: int,
    height: int,
    weights: SelectionWeights,
) -> float:
    return selection_components(
        instance, width=width, height=height, weights=weights
    )["final_score"]


def _centre_inside_region(
    bbox: list[float] | None,
    region: list[float],
) -> bool:
    if bbox is None or len(bbox) < 4:
        return False
    centre_x, centre_y = bbox_centre(bbox)
    return (
        float(region[0]) <= centre_x <= float(region[2])
        and float(region[1]) <= centre_y <= float(region[3])
    )


def select_primary_athlete(
    instances: list[dict[str, Any]],
    *,
    width: int,
    height: int,
    weights: SelectionWeights | None = None,
    override_track_id: str | None = None,
    region_of_interest: list[float] | None = None,
) -> SelectionResult:
    """Pick the most likely target athlete from one frame's instances.

    ``override_track_id`` implements the manual override: when it matches
    an instance it wins outright. ``region_of_interest`` (pixel-space
    ``[x1, y1, x2, y2]``) narrows candidates to those centred inside the
    region — the hook for event-specific positions such as a race lane —
    falling back to all candidates when nobody is inside it.
    """
    weights = weights or SelectionWeights()

    if override_track_id is not None:
        for index, instance in enumerate(instances):
            if str(instance.get("track_id")) == str(override_track_id):
                components = selection_components(
                    instance, width=width, height=height, weights=weights
                )
                return SelectionResult(
                    instance=instance,
                    score=components["final_score"],
                    reason="manual_override",
                    selected_index=index,
                    components=components,
                    candidate_scores=(components["final_score"],),
                    candidate_components=(components,),
                )

    candidates = [
        (index, instance)
        for index, instance in enumerate(instances)
        if not instance.get("detector_fallback", False)
    ]
    if not candidates:
        # A full-frame fallback pose is still usable when it is all we have.
        candidates = list(enumerate(instances))

    if region_of_interest is not None:
        inside = [
            (index, instance)
            for index, instance in candidates
            if _centre_inside_region(
                instance.get("bounding_box"), region_of_interest
            )
        ]
        if inside:
            candidates = inside

    if not candidates:
        return SelectionResult(
            instance=None, score=0.0, reason="none_available"
        )

    components = tuple(
        selection_components(
            instance, width=width, height=height, weights=weights
        )
        for _, instance in candidates
    )
    scores = tuple(item["final_score"] for item in components)
    best = max(range(len(candidates)), key=lambda index: scores[index])
    return SelectionResult(
        instance=candidates[best][1],
        score=scores[best],
        reason="scored",
        selected_index=candidates[best][0],
        components=components[best],
        candidate_scores=scores,
        candidate_components=components,
    )


def landmark_similarity(
    first: dict[str, Any],
    second: dict[str, Any],
    *,
    maximum_mean_shift: float = 0.25,
) -> float:
    """Similarity of two instances' shared named landmarks.

    Landmark coordinates are already normalized to the frame, so the mean
    shift is frame-size independent; a mean shift at or beyond
    ``maximum_mean_shift`` of the frame scores 0.
    """
    first_points = instance_keypoints(first)
    second_points = instance_keypoints(second)
    shared = set(first_points) & set(second_points)
    if not shared:
        return 0.0

    total_shift = 0.0
    for name in shared:
        total_shift += math.hypot(
            float(first_points[name]["x"]) - float(second_points[name]["x"]),
            float(first_points[name]["y"]) - float(second_points[name]["y"]),
        )
    mean_shift = total_shift / len(shared)
    if maximum_mean_shift <= 0.0:
        return 0.0
    return max(1.0 - mean_shift / maximum_mean_shift, 0.0)


def match_components(
    candidate: dict[str, Any],
    target: dict[str, Any],
    *,
    width: int,
    height: int,
    weights: TrackerWeights,
) -> dict[str, float]:
    """Component scores for how likely ``candidate`` is ``target``.

    The track-id component only helps while the worker emits a persistent
    identity; the current worker derives track_id from the detection index,
    which can swap between frames, so its weight stays low until a real
    tracker (ByteTrack / BoT-SORT) provides stable ids.
    """
    candidate_bbox = candidate.get("bounding_box")
    target_bbox = target.get("bounding_box")

    overlap = bbox_iou(candidate_bbox, target_bbox)

    motion_score = 0.0
    if (
        candidate_bbox is not None
        and target_bbox is not None
        and len(candidate_bbox) >= 4
        and len(target_bbox) >= 4
    ):
        diagonal = math.hypot(width, height)
        # Movement beyond a quarter of the frame diagonal between two
        # consecutive frames is treated as a different person.
        maximum_shift = diagonal / 4.0
        candidate_centre = bbox_centre(candidate_bbox)
        target_centre = bbox_centre(target_bbox)
        distance = math.hypot(
            candidate_centre[0] - target_centre[0],
            candidate_centre[1] - target_centre[1],
        )
        if maximum_shift > 0.0:
            motion_score = max(1.0 - distance / maximum_shift, 0.0)

    candidate_area = bbox_area(candidate_bbox)
    target_area = bbox_area(target_bbox)
    size_score = 0.0
    if candidate_area > 0.0 and target_area > 0.0:
        size_score = min(candidate_area, target_area) / max(
            candidate_area, target_area
        )

    similarity = landmark_similarity(candidate, target)

    track_id_score = 0.0
    candidate_track_id = candidate.get("track_id")
    target_track_id = target.get("track_id")
    if (
        candidate_track_id is not None
        and target_track_id is not None
        and str(candidate_track_id) == str(target_track_id)
    ):
        track_id_score = 1.0

    total = weights.total()
    final = 0.0
    if total > 0.0:
        final = (
            weights.bounding_box_overlap * overlap
            + weights.centre_motion * motion_score
            + weights.size_similarity * size_score
            + weights.landmark_similarity * similarity
            + weights.track_id_match * track_id_score
        ) / total

    return {
        "bbox_overlap_score": overlap,
        "centre_motion_score": motion_score,
        "size_similarity_score": size_score,
        "landmark_similarity_score": similarity,
        "track_id_score": track_id_score,
        "final_score": final,
    }


def match_score(
    candidate: dict[str, Any],
    target: dict[str, Any],
    *,
    width: int,
    height: int,
    weights: TrackerWeights,
) -> float:
    """How likely ``candidate`` is the same athlete as ``target``."""
    return match_components(
        candidate, target, width=width, height=height, weights=weights
    )["final_score"]


@dataclass(slots=True)
class AthleteTracker:
    """Keeps the same athlete selected across frames.

    Frame 1 (or any frame where the target is lost) selects the primary
    athlete; later frames match candidates against the current target and
    only re-select after ``maximum_missed_frames`` consecutive misses.
    """

    width: int
    height: int
    selection_weights: SelectionWeights = field(default_factory=SelectionWeights)
    tracker_weights: TrackerWeights = field(default_factory=TrackerWeights)
    minimum_match_score: float = 0.30
    maximum_missed_frames: int = 5
    override_track_id: str | None = None
    region_of_interest: list[float] | None = None
    _target: dict[str, Any] | None = None
    _missed_frames: int = 0

    def force_target(self, instance: dict[str, Any]) -> None:
        """Manual override: lock tracking onto a caller-chosen instance."""
        self._target = instance
        self._missed_frames = 0

    def reset(self) -> None:
        self._target = None
        self._missed_frames = 0

    def _select(self, instances: list[dict[str, Any]], *, frame_index: int,
                reason: str) -> TrackedSelection:
        result = select_primary_athlete(
            instances,
            width=self.width,
            height=self.height,
            weights=self.selection_weights,
            override_track_id=self.override_track_id,
            region_of_interest=self.region_of_interest,
        )
        if result.instance is None:
            self._missed_frames += 1
            return TrackedSelection(
                instance=None,
                score=0.0,
                reason="lost",
                frame_index=frame_index,
            )
        self._target = result.instance
        self._missed_frames = 0
        return TrackedSelection(
            instance=result.instance,
            score=result.score,
            reason=reason,
            frame_index=frame_index,
            components=result.components,
        )

    def update(
        self,
        instances: list[dict[str, Any]],
        *,
        frame_index: int,
    ) -> TrackedSelection:
        if self._target is None:
            return self._select(
                instances, frame_index=frame_index, reason="selected"
            )

        best_instance: dict[str, Any] | None = None
        best_components: dict[str, float] | None = None
        best_score = 0.0
        for instance in instances:
            components = match_components(
                instance,
                self._target,
                width=self.width,
                height=self.height,
                weights=self.tracker_weights,
            )
            if components["final_score"] > best_score:
                best_score = components["final_score"]
                best_instance = instance
                best_components = components

        if best_instance is not None and best_score >= self.minimum_match_score:
            self._target = best_instance
            self._missed_frames = 0
            return TrackedSelection(
                instance=best_instance,
                score=best_score,
                reason="tracked",
                frame_index=frame_index,
                components=best_components,
            )

        self._missed_frames += 1
        if self._missed_frames <= self.maximum_missed_frames:
            # Keep reporting the last confirmed target while it is briefly
            # occluded or dropped by the detector.
            return TrackedSelection(
                instance=self._target,
                score=best_score,
                reason="coasting",
                frame_index=frame_index,
                components=best_components,
            )

        self._target = None
        return self._select(
            instances, frame_index=frame_index, reason="reselected"
        )

    def update_from_response(
        self,
        response: dict[str, Any],
        *,
        frame_index: int,
    ) -> TrackedSelection:
        """Feed an RTMPose worker response directly.

        Frame dimensions are adopted from the response, so preprocessing
        that changes resolution mid-stream cannot skew the geometry
        scores.
        """
        width = response.get("width")
        height = response.get("height")
        if width and height:
            self.width = int(width)
            self.height = int(height)
        return self.update(
            response.get("instances", []), frame_index=frame_index
        )
