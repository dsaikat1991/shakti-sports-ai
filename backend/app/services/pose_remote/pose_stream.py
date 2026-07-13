from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.pose_adapters.models import (
    UnifiedKeypoint,
    UnifiedPoseFrame,
)


@dataclass(slots=True, frozen=True)
class PoseGap:
    """A run of consecutive non-observed frames in a tracked timeline.

    Gap frames are never silently dropped or duplicated: they are recorded
    here so downstream engines can decide to interpolate, predict, or
    exclude the span.
    """

    frame_indices: tuple[int, ...]
    timestamps_ms: tuple[int, ...]
    reasons: tuple[str, ...]

    @property
    def start_frame_index(self) -> int:
        return self.frame_indices[0]

    @property
    def end_frame_index(self) -> int:
        return self.frame_indices[-1]

    @property
    def frame_count(self) -> int:
        return len(self.frame_indices)


@dataclass(slots=True, frozen=True)
class PoseStream:
    """One clean, time-ordered landmark stream for the target athlete."""

    frames: tuple[UnifiedPoseFrame, ...]
    gaps: tuple[PoseGap, ...]
    image_width: int | None
    image_height: int | None
    fps: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PoseSegment:
    """A continuous run of pose frames with no unfilled gap inside it.

    Motion quantities (velocity, cadence, contact events) are only
    meaningful within one segment: an unfilled gap can hide an editing
    cut or a lost athlete, so nothing may be computed across it.
    """

    frames: tuple[UnifiedPoseFrame, ...]

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def start_frame_index(self) -> int:
        return self.frames[0].frame_index

    @property
    def end_frame_index(self) -> int:
        return self.frames[-1].frame_index

    @property
    def duration_ms(self) -> int:
        return self.frames[-1].timestamp_ms - self.frames[0].timestamp_ms


def _record_timestamp(record: dict[str, Any]) -> int:
    # When the source video has no usable fps the pipeline leaves
    # timestamp_ms empty; fall back to the frame index so ordering and
    # gap spans keep working (flagged in the stream metadata).
    timestamp = record.get("timestamp_ms")
    if timestamp is None:
        return int(record["frame_index"])
    return int(timestamp)


def record_to_pose_frame(
    record: dict[str, Any],
    *,
    image_width: int | None,
    image_height: int | None,
) -> UnifiedPoseFrame:
    keypoints = tuple(
        UnifiedKeypoint(
            name=str(name),
            x=float(point["x"]),
            y=float(point["y"]),
            z=(
                float(point["z"])
                if point.get("z") is not None
                else None
            ),
            confidence=(
                float(point["confidence"])
                if point.get("confidence") is not None
                else None
            ),
        )
        for name, point in record.get("landmarks", {}).items()
    )
    return UnifiedPoseFrame(
        backend="rtmpose",
        frame_index=int(record["frame_index"]),
        timestamp_ms=_record_timestamp(record),
        keypoints=keypoints,
        image_width=image_width,
        image_height=image_height,
        metadata={
            "tracking_status": record.get("tracking_status"),
            "tracking_score": record.get("tracking_score"),
            "track_id": record.get("track_id"),
            "bounding_box": record.get("bounding_box"),
        },
    )


def timeline_to_pose_stream(
    pipeline_result: dict[str, Any],
) -> PoseStream:
    """Convert a tracked-video pipeline result into a :class:`PoseStream`.

    Only ``is_observed`` records become pose frames; coasting, lost, and
    error records are collapsed into explicit :class:`PoseGap` runs.
    """
    video = pipeline_result.get("video", {})
    image_width = video.get("width") or None
    image_height = video.get("height") or None
    fps = float(video.get("fps") or 0.0)

    records = sorted(
        pipeline_result.get("frames", []),
        key=lambda record: record["frame_index"],
    )

    frames: list[UnifiedPoseFrame] = []
    gaps: list[PoseGap] = []
    gap_run: list[dict[str, Any]] = []

    def close_gap_run() -> None:
        if not gap_run:
            return
        gaps.append(
            PoseGap(
                frame_indices=tuple(
                    int(record["frame_index"]) for record in gap_run
                ),
                timestamps_ms=tuple(
                    _record_timestamp(record) for record in gap_run
                ),
                reasons=tuple(
                    str(record.get("tracking_status")) for record in gap_run
                ),
            )
        )
        gap_run.clear()

    for record in records:
        if record.get("is_observed"):
            close_gap_run()
            frames.append(
                record_to_pose_frame(
                    record,
                    image_width=image_width,
                    image_height=image_height,
                )
            )
        else:
            gap_run.append(record)
    close_gap_run()

    gap_frames = sum(gap.frame_count for gap in gaps)
    total = len(frames) + gap_frames
    return PoseStream(
        frames=tuple(frames),
        gaps=tuple(gaps),
        image_width=image_width,
        image_height=image_height,
        fps=fps,
        metadata={
            "observed_frames": len(frames),
            "gap_frames": gap_frames,
            "observed_ratio": (
                round(len(frames) / total, 4) if total else 0.0
            ),
            "interpolated_frames": 0,
            "timestamps_are_frame_indices": fps <= 0.0,
        },
    )


def _interpolate_keypoints(
    previous: UnifiedPoseFrame,
    following: UnifiedPoseFrame,
    *,
    alpha: float,
) -> tuple[UnifiedKeypoint, ...]:
    following_map = following.keypoint_map()
    keypoints: list[UnifiedKeypoint] = []
    for start in previous.keypoints:
        end = following_map.get(start.name)
        if end is None:
            continue
        z = None
        if start.z is not None and end.z is not None:
            z = start.z + (end.z - start.z) * alpha
        confidence = None
        if start.confidence is not None and end.confidence is not None:
            confidence = min(start.confidence, end.confidence)
        keypoints.append(
            UnifiedKeypoint(
                name=start.name,
                x=start.x + (end.x - start.x) * alpha,
                y=start.y + (end.y - start.y) * alpha,
                z=z,
                confidence=confidence,
            )
        )
    return tuple(keypoints)


def _interpolate_gap(
    gap: PoseGap,
    previous: UnifiedPoseFrame,
    following: UnifiedPoseFrame,
    *,
    stream: PoseStream,
) -> tuple[UnifiedPoseFrame, ...] | None:
    span = following.timestamp_ms - previous.timestamp_ms
    if span <= 0:
        return None

    frames: list[UnifiedPoseFrame] = []
    for frame_index, timestamp_ms, reason in zip(
        gap.frame_indices, gap.timestamps_ms, gap.reasons, strict=True
    ):
        alpha = (timestamp_ms - previous.timestamp_ms) / span
        keypoints = _interpolate_keypoints(
            previous, following, alpha=alpha
        )
        if not keypoints:
            return None
        frames.append(
            UnifiedPoseFrame(
                backend="rtmpose",
                frame_index=frame_index,
                timestamp_ms=timestamp_ms,
                keypoints=keypoints,
                image_width=stream.image_width,
                image_height=stream.image_height,
                metadata={
                    "interpolated": True,
                    "gap_reason": reason,
                    "source_frame_indices": [
                        previous.frame_index,
                        following.frame_index,
                    ],
                },
            )
        )
    return tuple(frames)


def fill_gaps(
    stream: PoseStream,
    *,
    max_gap_ms: int,
) -> PoseStream:
    """Linearly interpolate landmarks across short gaps.

    A gap is only bridged when observed frames exist on both sides and
    they are at most ``max_gap_ms`` apart; interpolated frames are stamped
    ``metadata={"interpolated": True, ...}`` so downstream engines can
    always tell reconstruction from observation. Longer gaps stay in
    ``gaps`` untouched. When the stream has no real timestamps
    (``timestamps_are_frame_indices``), ``max_gap_ms`` counts frames.
    """
    frames = list(stream.frames)
    remaining: list[PoseGap] = []
    interpolated = int(stream.metadata.get("interpolated_frames", 0))

    for gap in stream.gaps:
        previous: UnifiedPoseFrame | None = None
        following: UnifiedPoseFrame | None = None
        for frame in frames:
            if frame.frame_index < gap.start_frame_index:
                if previous is None or frame.frame_index > previous.frame_index:
                    previous = frame
            elif frame.frame_index > gap.end_frame_index:
                if following is None or frame.frame_index < following.frame_index:
                    following = frame

        if previous is None or following is None:
            remaining.append(gap)
            continue
        if following.timestamp_ms - previous.timestamp_ms > max_gap_ms:
            remaining.append(gap)
            continue

        new_frames = _interpolate_gap(
            gap, previous, following, stream=stream
        )
        if new_frames is None:
            remaining.append(gap)
            continue
        frames.extend(new_frames)
        interpolated += len(new_frames)

    frames.sort(key=lambda frame: frame.frame_index)
    metadata = dict(stream.metadata)
    metadata["interpolated_frames"] = interpolated
    return PoseStream(
        frames=tuple(frames),
        gaps=tuple(remaining),
        image_width=stream.image_width,
        image_height=stream.image_height,
        fps=stream.fps,
        metadata=metadata,
    )


def split_into_segments(
    stream: PoseStream,
    *,
    minimum_frames: int = 1,
) -> tuple[PoseSegment, ...]:
    """Split a stream into continuous segments at its unfilled gaps.

    Run :func:`fill_gaps` first so short, bridgeable gaps do not split
    the stream; whatever gaps remain (editing cuts, long occlusions,
    lost athlete) become segment boundaries. Segments shorter than
    ``minimum_frames`` are dropped — a few stranded frames between two
    cuts carry no usable motion signal.
    """
    if not stream.frames:
        return ()

    segments: list[PoseSegment] = []
    current: list[UnifiedPoseFrame] = [stream.frames[0]]
    for previous, frame in zip(stream.frames, stream.frames[1:]):
        has_gap_between = any(
            previous.frame_index < gap.start_frame_index
            and gap.end_frame_index < frame.frame_index
            for gap in stream.gaps
        )
        if has_gap_between:
            segments.append(PoseSegment(frames=tuple(current)))
            current = []
        current.append(frame)
    segments.append(PoseSegment(frames=tuple(current)))

    return tuple(
        segment
        for segment in segments
        if segment.frame_count >= minimum_frames
    )
