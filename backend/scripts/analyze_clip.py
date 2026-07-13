from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from app.services.pose_remote.client import RTMPoseWorkerClient
from app.services.pose_remote.pose_stream import (
    fill_gaps,
    timeline_to_pose_stream,
)
from app.services.pose_remote.video_pipeline import analyze_video_with_tracking

STATUS_LETTERS = {
    "selected": "S",
    "tracked": "T",
    "reselected": "R",
    "coasting": "c",
    "lost": "x",
    "error": "!",
}


class ProgressWorker:
    """Wraps the worker client to print progress during long clips."""

    def __init__(self, client: RTMPoseWorkerClient, expected_frames: int) -> None:
        self.client = client
        self.expected_frames = expected_frames
        self.processed = 0
        self.started = time.perf_counter()

    def infer_image_bytes(self, **kwargs) -> dict:
        response = self.client.infer_image_bytes(**kwargs)
        self.processed += 1
        if self.processed % 25 == 0 or self.processed == self.expected_frames:
            elapsed = time.perf_counter() - self.started
            per_frame = elapsed / self.processed
            remaining = max(self.expected_frames - self.processed, 0) * per_frame
            print(
                f"  {self.processed}/{self.expected_frames} frames"
                f" | {per_frame * 1000:.0f} ms/frame"
                f" | ~{remaining:.0f}s remaining",
                flush=True,
            )
        return response


def count_expected_frames(
    video_path: Path, *, frame_stride: int, max_frames: int | None
) -> int:
    capture = cv2.VideoCapture(str(video_path))
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    expected = (total + frame_stride - 1) // frame_stride if total > 0 else 0
    if max_frames is not None:
        expected = min(expected, max_frames)
    return expected


def write_annotated_video(
    video_path: Path,
    records: list[dict],
    output_path: Path,
    *,
    frame_stride: int,
    fps: float,
) -> None:
    records_by_index = {record["frame_index"]: record for record in records}
    capture = cv2.VideoCapture(str(video_path))
    writer = None
    frame_index = -1
    try:
        while True:
            grabbed, frame = capture.read()
            if not grabbed:
                break
            frame_index += 1
            record = records_by_index.get(frame_index)
            if record is None:
                continue
            height, width = frame.shape[:2]
            if writer is None:
                writer = cv2.VideoWriter(
                    str(output_path),
                    cv2.VideoWriter_fourcc(*"MJPG"),
                    max(fps / frame_stride, 1.0),
                    (width, height),
                )

            observed = record["is_observed"]
            colour = (0, 220, 0) if observed else (0, 200, 255)
            bbox = record["bounding_box"]
            if bbox:
                cv2.rectangle(
                    frame,
                    (int(bbox[0]), int(bbox[1])),
                    (int(bbox[2]), int(bbox[3])),
                    colour,
                    2,
                )
            for point in record["landmarks"].values():
                cv2.circle(
                    frame,
                    (int(point["x"] * width), int(point["y"] * height)),
                    4,
                    colour,
                    -1,
                )
            label = (
                f"frame {record['frame_index']}"
                f" | {record['tracking_status']}"
                f" | score {record['tracking_score']:.2f}"
            )
            cv2.putText(
                frame,
                label,
                (12, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                colour,
                2,
            )
            writer.write(frame)
    finally:
        capture.release()
        if writer is not None:
            writer.release()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the tracked RTMPose pipeline on a video clip."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Process every Nth frame (default 1 = every frame).",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Stop after this many sampled frames.",
    )
    parser.add_argument(
        "--max-gap-ms",
        type=int,
        default=300,
        help="Interpolate gaps up to this long (default 300).",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Write the full timeline result to this JSON file.",
    )
    parser.add_argument(
        "--annotate",
        type=Path,
        default=None,
        help="Write an annotated .avi with bbox + landmarks drawn.",
    )
    args = parser.parse_args()

    client = RTMPoseWorkerClient()
    health = client.health()
    print(
        f"worker: {health['status']}"
        f" | {health['model_name']} on {health['device']}"
        f" | mmpose {health['mmpose_version']}"
    )
    client.initialize()

    expected = count_expected_frames(
        args.video, frame_stride=args.stride, max_frames=args.max_frames
    )
    print(f"processing ~{expected} sampled frames...")

    started = time.perf_counter()
    result = analyze_video_with_tracking(
        args.video,
        worker=ProgressWorker(client, expected),
        frame_stride=args.stride,
        max_frames=args.max_frames,
    )
    elapsed = time.perf_counter() - started

    video = result["video"]
    frames = result["frames"]
    print(
        f"\nvideo: {video['width']}x{video['height']}"
        f" @ {video['fps']} fps"
        f" | {video['total_frames']} frames"
        f" | sampled {video['sampled_frames']} (stride {args.stride})"
    )
    print(
        f"processed in {elapsed:.1f}s"
        f" ({elapsed * 1000 / max(len(frames), 1):.0f} ms per sampled frame)"
    )

    strip = "".join(
        STATUS_LETTERS.get(record["tracking_status"], "?")
        for record in frames
    )
    print("\ntimeline (S/T/R observed, c coasting, x lost, ! error):")
    for offset in range(0, len(strip), 60):
        print(f"  {offset:5d}  {strip[offset:offset + 60]}")

    print("\nsummary:", result["summary"])

    observed_scores = [
        record["tracking_score"] for record in frames if record["is_observed"]
    ]
    if observed_scores:
        print(
            "tracking score (observed frames):"
            f" min {min(observed_scores):.3f}"
            f" | mean {sum(observed_scores) / len(observed_scores):.3f}"
        )

    stream = timeline_to_pose_stream(result)
    filled = fill_gaps(stream, max_gap_ms=args.max_gap_ms)
    print(
        f"\npose stream: {stream.metadata['observed_frames']} observed"
        f" | {len(stream.gaps)} gap(s)"
        f" ({stream.metadata['gap_frames']} frames)"
        f" | after fill_gaps({args.max_gap_ms}ms):"
        f" {filled.metadata['interpolated_frames']} interpolated,"
        f" {len(filled.gaps)} gap(s) left"
    )
    for gap in stream.gaps:
        print(
            f"  gap frames {gap.start_frame_index}-{gap.end_frame_index}"
            f" ({gap.frame_count} frames, reasons {set(gap.reasons)})"
        )

    if args.json:
        args.json.write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        print(f"\nfull timeline written to {args.json}")

    if args.annotate:
        write_annotated_video(
            args.video,
            frames,
            args.annotate,
            frame_stride=args.stride,
            fps=video["fps"] or 10.0,
        )
        print(f"annotated video written to {args.annotate}")


if __name__ == "__main__":
    main()
