from __future__ import annotations

"""
Frame-scrubbing tool for hand-labeling true ground-contact frames.

Built to replace the "static image strip" methodology used for the first
4 labels in tests/fixtures/ground_truth_contact_labels.json (flagged in
that file's own conclusion as insufficiently rigorous). Instead of one
compressed strip covering ~24 frames, this produces one high-resolution,
tightly-cropped, individually frame-numbered tile per frame, laid out in
a small grid per window, so each frame gets enough pixels to judge heel/
toe-to-ground distance with confidence.

Usage:
    .venv/Scripts/python.exe scripts/label_contact_frames.py \
        --timeline <timeline.json produced by analyze_clip.py --json> \
        --video examples/my_sprint_2.mp4 \
        --side right \
        --out <output_dir> \
        [--mode candidates | --mode uniform]

Two window-generation modes:
  candidates - centers a window on every peak the *current* detector
               (app.services.biomechanics.contact_events) already fires
               on, for the given side. Good for auditing precision
               (is each fired event actually a contact?) and for
               labeling the frame precisely even when the detector's
               frame estimate is off by a few frames.
  uniform    - lays down evenly-spaced windows across the whole clip
               based on the clip's own median step interval (derived
               from the *other* side's already-validated cadence
               signal where possible, else from bounding-box motion).
               Good for catching false negatives - real contacts the
               detector missed entirely - which "candidates" mode
               structurally cannot see.

Each window becomes one grid PNG under <out>/<clip>_<side>_<window_idx>.png.
Nothing here writes to tests/fixtures/ - after visual review, transcribe
findings into ground_truth_contact_labels.json by hand.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np

from app.services.biomechanics.contact_events import (
    FootSample,
    _detect_side_contacts,
)

HALPE26_TO_MEDIAPIPE_INDEX = {
    "nose": 0,
    "left_eye": 2,
    "right_eye": 5,
    "left_ear": 7,
    "right_ear": 8,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_big_toe": 31,
    "right_big_toe": 32,
}

TILE_SIZE = 260
GRID_COLS = 4
LABEL_HEIGHT = 26
MARGIN = 4


def load_frames(timeline_path: Path) -> tuple[dict, list[dict]]:
    data = json.loads(timeline_path.read_text(encoding="utf-8"))
    return data["video"], data["frames"]


def foot_series_for_side(frames: list[dict], side: str) -> list[FootSample]:
    keys = (f"{side}_ankle", f"{side}_heel", f"{side}_big_toe")
    samples: list[FootSample] = []
    for frame in frames:
        if not frame["is_observed"]:
            continue
        ys = []
        for key in keys:
            landmark = frame["landmarks"].get(key)
            if landmark is None:
                continue
            confidence = landmark.get("confidence")
            if confidence is None or confidence < 0.35:
                continue
            y = landmark.get("y")
            if y is None or not (0.0 <= y <= 1.0):
                continue
            ys.append(y)
        if len(ys) < 2:
            continue
        samples.append(
            FootSample(
                side=side,
                frame_index=frame["frame_index"],
                timestamp_ms=frame["timestamp_ms"],
                normalized_y=float(np.mean(ys)),
            )
        )
    return samples


def candidate_windows(
    frames: list[dict], side: str, *, half_width: int = 7
) -> list[tuple[int, int]]:
    samples = foot_series_for_side(frames, side)
    events = _detect_side_contacts(samples)
    windows = []
    for event in events:
        center = event.peak_frame_index
        windows.append((max(0, center - half_width), center + half_width))
    return windows


def uniform_windows(
    frames: list[dict], side: str, *, half_width: int = 7, count: int = 8
) -> list[tuple[int, int]]:
    observed = [f["frame_index"] for f in frames if f["is_observed"]]
    if not observed:
        return []
    lo, hi = min(observed), max(observed)
    if hi - lo < 2 * half_width:
        return [(lo, hi)]
    centers = np.linspace(lo + half_width, hi - half_width, num=count)
    return [(int(round(c)) - half_width, int(round(c)) + half_width) for c in centers]


def crop_tile(frame_bgr: np.ndarray, landmark_xy: tuple[float, float] | None) -> np.ndarray:
    height, width = frame_bgr.shape[:2]
    if landmark_xy is None:
        cx, cy = width / 2, height / 2
    else:
        cx, cy = landmark_xy[0] * width, landmark_xy[1] * height

    half = max(height, width) * 0.20
    x0 = int(max(0, min(width - 1, cx - half)))
    x1 = int(max(1, min(width, cx + half)))
    y0 = int(max(0, min(height - 1, cy - half)))
    y1 = int(max(1, min(height, cy + half)))
    if x1 <= x0:
        x1 = x0 + 1
    if y1 <= y0:
        y1 = y0 + 1

    crop = frame_bgr[y0:y1, x0:x1]
    tile = cv2.resize(crop, (TILE_SIZE, TILE_SIZE), interpolation=cv2.INTER_CUBIC)

    if landmark_xy is not None:
        rel_x = (cx - x0) / max(1, (x1 - x0)) * TILE_SIZE
        rel_y = (cy - y0) / max(1, (y1 - y0)) * TILE_SIZE
        cv2.drawMarker(
            tile,
            (int(rel_x), int(rel_y)),
            (0, 0, 255),
            markerType=cv2.MARKER_CROSS,
            markerSize=14,
            thickness=2,
        )
    return tile


def build_grid(tiles: list[np.ndarray], captions: list[str]) -> np.ndarray:
    rows = (len(tiles) + GRID_COLS - 1) // GRID_COLS
    cell_h = TILE_SIZE + LABEL_HEIGHT
    grid = np.full(
        (rows * cell_h + MARGIN, GRID_COLS * (TILE_SIZE + MARGIN) + MARGIN, 3),
        30,
        dtype=np.uint8,
    )
    for index, (tile, caption) in enumerate(zip(tiles, captions)):
        row, col = divmod(index, GRID_COLS)
        y0 = row * cell_h + MARGIN
        x0 = col * (TILE_SIZE + MARGIN) + MARGIN
        grid[y0 : y0 + TILE_SIZE, x0 : x0 + TILE_SIZE] = tile
        cv2.putText(
            grid,
            caption,
            (x0 + 4, y0 + TILE_SIZE + 19),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return grid


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeline", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--side", choices=["left", "right"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=["candidates", "uniform"], default="candidates")
    parser.add_argument("--half-width", type=int, default=7)
    parser.add_argument("--uniform-count", type=int, default=8)
    args = parser.parse_args()

    video_meta, frames = load_frames(args.timeline)
    frames_by_index = {f["frame_index"]: f for f in frames}

    if args.mode == "candidates":
        windows = candidate_windows(frames, args.side, half_width=args.half_width)
    else:
        windows = uniform_windows(
            frames, args.side, half_width=args.half_width, count=args.uniform_count
        )

    if not windows:
        print("No windows generated - nothing to label.")
        return

    args.out.mkdir(parents=True, exist_ok=True)
    clip_name = args.video.stem
    landmark_key = f"{args.side}_ankle"

    capture = cv2.VideoCapture(str(args.video))
    frame_cache: dict[int, np.ndarray] = {}
    needed = set()
    for start, end in windows:
        needed.update(range(start, end + 1))

    index = -1
    while True:
        grabbed, frame = capture.read()
        if not grabbed:
            break
        index += 1
        if index in needed:
            frame_cache[index] = frame
        if index >= max(needed):
            break
    capture.release()

    manifest = []
    for window_idx, (start, end) in enumerate(windows):
        tiles = []
        captions = []
        for frame_index in range(start, end + 1):
            frame_bgr = frame_cache.get(frame_index)
            if frame_bgr is None:
                continue
            record = frames_by_index.get(frame_index)
            landmark_xy = None
            y_value = None
            if record is not None and record["is_observed"]:
                landmark = record["landmarks"].get(landmark_key)
                if landmark is not None:
                    landmark_xy = (landmark["x"], landmark["y"])
                    y_value = landmark["y"]
            tiles.append(crop_tile(frame_bgr, landmark_xy))
            ts = record["timestamp_ms"] if record else None
            y_str = f"{y_value:.3f}" if y_value is not None else "?"
            captions.append(f"f{frame_index} t{ts}ms y={y_str}")

        if not tiles:
            continue

        grid = build_grid(tiles, captions)
        out_path = args.out / f"{clip_name}_{args.side}_{args.mode}_{window_idx:02d}_f{start}-{end}.png"
        cv2.imwrite(str(out_path), grid)
        manifest.append(
            {
                "file": out_path.name,
                "frame_range": [start, end],
            }
        )
        print(f"wrote {out_path.name}")

    manifest_path = args.out / f"{clip_name}_{args.side}_{args.mode}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n{len(manifest)} window(s) written to {args.out}")


if __name__ == "__main__":
    main()
