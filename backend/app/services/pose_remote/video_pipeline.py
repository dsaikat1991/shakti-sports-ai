from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import cv2

from app.services.pose_remote.athlete_selection import (
    AthleteTracker,
    instance_keypoints,
)


class PoseWorker(Protocol):
    def infer_image_bytes(
        self,
        *,
        content: bytes,
        filename: str = "frame.jpg",
    ) -> dict[str, Any]:
        ...


MAXIMUM_CONSECUTIVE_ERRORS = 5


def frame_record(
    *,
    frame_index: int,
    timestamp_ms: int | None,
    tracked: Any,
    warnings: list[str],
) -> dict[str, Any]:
    instance = tracked.instance
    return {
        "frame_index": frame_index,
        "timestamp_ms": timestamp_ms,
        "tracking_status": tracked.reason,
        "tracking_score": round(float(tracked.score), 4),
        "is_observed": tracked.is_observed,
        "track_id": instance.get("track_id") if instance else None,
        "bounding_box": instance.get("bounding_box") if instance else None,
        "landmarks": instance_keypoints(instance) if instance else {},
        "components": tracked.components,
        "warnings": warnings,
    }


def analyze_video_with_tracking(
    video_path: str | Path,
    *,
    worker: PoseWorker,
    tracker: AthleteTracker | None = None,
    frame_stride: int = 1,
    max_frames: int | None = None,
    jpeg_quality: int = 90,
) -> dict[str, Any]:
    """Run tracked pose inference over a video.

    Decodes the video, samples every ``frame_stride``-th frame, sends each
    sampled frame to the RTMPose worker, and keeps the same athlete
    selected across frames with an :class:`AthleteTracker`. Only records
    with ``is_observed`` set should be consumed as fresh biomechanics
    samples; ``coasting`` frames repeat the last confirmed pose and must be
    treated as missing/interpolated by downstream engines.
    """
    if frame_stride < 1:
        raise ValueError("frame_stride must be at least 1.")

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # Frame dimensions are adopted per response inside the tracker, so a
    # placeholder size is fine until the first frame arrives.
    tracker = tracker or AthleteTracker(width=0, height=0)

    frames: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}
    consecutive_errors = 0
    frame_index = -1

    try:
        while True:
            grabbed, frame = capture.read()
            if not grabbed:
                break
            frame_index += 1
            if frame_index % frame_stride != 0:
                continue
            if max_frames is not None and len(frames) >= max_frames:
                break

            timestamp_ms = (
                round(frame_index * 1000.0 / fps) if fps and fps > 0 else None
            )

            encoded, buffer = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)],
            )
            if not encoded:
                raise ValueError(
                    f"Could not encode frame {frame_index} as JPEG."
                )

            try:
                response = worker.infer_image_bytes(
                    content=buffer.tobytes(),
                    filename=f"frame_{frame_index:06d}.jpg",
                )
            except Exception as exc:
                consecutive_errors += 1
                if consecutive_errors > MAXIMUM_CONSECUTIVE_ERRORS:
                    raise RuntimeError(
                        "RTMPose worker failed on "
                        f"{consecutive_errors} consecutive frames; "
                        "aborting video analysis."
                    ) from exc
                record = {
                    "frame_index": frame_index,
                    "timestamp_ms": timestamp_ms,
                    "tracking_status": "error",
                    "tracking_score": 0.0,
                    "is_observed": False,
                    "track_id": None,
                    "bounding_box": None,
                    "landmarks": {},
                    "components": None,
                    "warnings": [str(exc)],
                }
                frames.append(record)
                status_counts["error"] = status_counts.get("error", 0) + 1
                continue

            consecutive_errors = 0
            tracked = tracker.update_from_response(
                response, frame_index=frame_index
            )
            record = frame_record(
                frame_index=frame_index,
                timestamp_ms=timestamp_ms,
                tracked=tracked,
                warnings=response.get("warnings", []),
            )
            frames.append(record)
            status_counts[tracked.reason] = (
                status_counts.get(tracked.reason, 0) + 1
            )
    finally:
        capture.release()

    observed = sum(1 for record in frames if record["is_observed"])
    return {
        "video": {
            "path": str(video_path),
            "fps": round(fps, 3) if fps else 0.0,
            "total_frames": total_frames,
            "frame_stride": frame_stride,
            "sampled_frames": len(frames),
            "width": tracker.width,
            "height": tracker.height,
        },
        "frames": frames,
        "summary": {
            "status_counts": status_counts,
            "observed_frames": observed,
            "observed_ratio": (
                round(observed / len(frames), 4) if frames else 0.0
            ),
        },
    }
