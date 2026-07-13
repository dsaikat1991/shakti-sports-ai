from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.pose_remote.athlete_selection import AthleteTracker
from app.services.pose_remote.biomechanics_bridge import analyze_sprint_stream
from app.services.pose_remote.client import RTMPoseWorkerClient
from app.services.pose_remote.pose_stream import timeline_to_pose_stream
from app.services.pose_remote.video_pipeline import analyze_video_with_tracking
from app.services.reports.sprint_segment_report import (
    build_sprint_stream_report,
    format_stream_report_text,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the full pipeline (RTMPose worker -> tracking -> pose "
            "stream -> biomechanics bridge -> report) on a sprint clip."
        )
    )
    parser.add_argument("video", type=Path)
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Process every Nth frame (default 1 = every frame).",
    )
    parser.add_argument(
        "--max-gap-ms",
        type=int,
        default=300,
        help="Interpolate gaps up to this long (default 300).",
    )
    parser.add_argument(
        "--minimum-segment-frames",
        type=int,
        default=30,
        help="Segments shorter than this are skipped (default 30).",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Write the full structured report to this JSON file.",
    )
    args = parser.parse_args()

    client = RTMPoseWorkerClient()
    health = client.health()
    print(
        f"worker: {health['status']}"
        f" | {health['model_name']} on {health['device']}"
    )
    client.initialize()

    print(f"processing {args.video} ...")
    timeline = analyze_video_with_tracking(
        args.video,
        worker=client,
        tracker=AthleteTracker(width=0, height=0),
        frame_stride=args.stride,
    )

    stream = timeline_to_pose_stream(timeline)
    analysis = analyze_sprint_stream(
        stream,
        max_gap_ms=args.max_gap_ms,
        minimum_segment_frames=args.minimum_segment_frames,
    )
    report = build_sprint_stream_report(analysis)

    print(
        f"\n{report['observed_frames']} observed frames"
        f" | {report['interpolated_frames']} interpolated"
        f" | {report['unbridged_gaps']} unbridged gap(s)"
        f" | {len(report['segments'])} segment(s)\n"
    )
    print(format_stream_report_text(report))

    if args.json:
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nfull report written to {args.json}")


if __name__ == "__main__":
    main()
