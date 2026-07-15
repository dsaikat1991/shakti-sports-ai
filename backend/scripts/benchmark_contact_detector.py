from __future__ import annotations

"""
Reproducible evaluation harness for ground-contact detection (see
datasets/sprint_biomechanics/README.md for the full workflow this fits
into). Runs the real, unmodified production detector
(app.services.biomechanics.contact_events) against a tracked timeline and
compares it to hand-labeled ground truth using
app.services.biomechanics.gait_event_evaluator - already-existing,
already-tested precision/recall/F1/timing-error code that had never been
connected to real ground truth before this tool existed.

Reuses label_contact_frames.load_frames/foot_series_for_side - the same
data path already used to generate the reviewed tiles, not a parallel
reimplementation.

event_type is always "initial_contact" here, on both the predicted and
actual side. "toe_off" is intentionally left empty: V1 ground-truth
labels are single-point contact judgments (matching the detector's own
peak_timestamp_ms), not full stance intervals. See the README's Phase 1
/ Phase 2 note. This is documented, not a bug - evaluate_by_event_type's
"toe_off" bucket will read 0/0 until interval labels exist.

Usage:
    .venv/Scripts/python.exe scripts/benchmark_contact_detector.py \
        --timeline timeline.json --labels labels/my_clip.json

    .venv/Scripts/python.exe scripts/benchmark_contact_detector.py \
        --manifest datasets/sprint_biomechanics/manifest.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.biomechanics.contact_events import ContactEvent, _detect_side_contacts
from app.services.biomechanics.gait_event_evaluator import evaluate_by_event_type
from app.services.biomechanics.gait_event_models import GaitEvent

from label_contact_frames import foot_series_for_side, load_frames

DATASET_ROOT = Path(__file__).resolve().parent.parent / "datasets" / "sprint_biomechanics"
DEFAULT_OUT_DIR = DATASET_ROOT / "benchmarks"

SIDES = ("left", "right")
TOE_OFF_NOTE = (
    "event_type 'toe_off' is intentionally empty in both predicted and actual - "
    "V1 labels are single-point contact judgments (matching the detector's own "
    "peak_timestamp_ms), not stance intervals. See "
    "datasets/sprint_biomechanics/README.md for the Phase 1/Phase 2 note."
)


def contact_events_to_gait_events(
    events: list[ContactEvent], side: str
) -> list[GaitEvent]:
    return [
        GaitEvent(
            event_type="initial_contact",
            side=side,
            timestamp_ms=event.peak_timestamp_ms,
            frame_index=event.peak_frame_index,
            confidence=event.confidence,
            source="contact_events_v1",
        )
        for event in events
    ]


def reviewed_predicted_frame_indices(label_data: dict, side: str) -> set[int]:
    """
    Every detector-fired peak_frame_index a human actually looked at and
    gave a verdict to (true_contact OR false_positive OR inconclusive OR
    unusable) for this side, regardless of verdict.
    """
    sides = label_data.get("label_sets", {}).get("ground_contact_peak", {}).get("sides", {})
    entries = sides.get(side, [])
    return {
        entry["detector_peak_frame_index"]
        for entry in entries
        if entry.get("detector_peak_frame_index") is not None
    }


def labels_to_gait_events(
    label_data: dict, side: str
) -> tuple[list[GaitEvent], dict[str, int]]:
    sides = label_data.get("label_sets", {}).get("ground_contact_peak", {}).get("sides", {})
    entries = sides.get(side, [])

    verdict_counts = {
        "true_contact": 0,
        "false_positive": 0,
        "inconclusive": 0,
        "unusable": 0,
    }
    gait_events: list[GaitEvent] = []

    for entry in entries:
        verdict = entry.get("verdict")
        if verdict in verdict_counts:
            verdict_counts[verdict] += 1

        if verdict == "true_contact" and entry.get("labeled_timestamp_ms") is not None:
            gait_events.append(
                GaitEvent(
                    event_type="initial_contact",
                    side=side,
                    timestamp_ms=int(entry["labeled_timestamp_ms"]),
                    frame_index=entry.get("labeled_frame_index"),
                    confidence=None,
                    source="human_label",
                )
            )

    return gait_events, verdict_counts


def collect_clip_events(
    timeline_path: Path, labels_path: Path
) -> tuple[
    str,
    dict[str, list[GaitEvent]],
    dict[str, list[GaitEvent]],
    dict[str, dict[str, int]],
    dict[str, dict[str, int]],
]:
    _video_meta, frames = load_frames(timeline_path)
    label_data = json.loads(labels_path.read_text(encoding="utf-8"))
    clip_id = label_data.get("clip_id", timeline_path.stem)

    predicted_by_side: dict[str, list[GaitEvent]] = {}
    actual_by_side: dict[str, list[GaitEvent]] = {}
    verdict_summary: dict[str, dict[str, int]] = {}
    coverage: dict[str, dict[str, int]] = {}

    for side in SIDES:
        samples = foot_series_for_side(frames, side)
        contact_events = _detect_side_contacts(samples)

        # Restricted to detector firings a human actually reviewed. An
        # unreviewed detector event is neither a confirmed hit nor a
        # confirmed miss - counting it as a false positive by default
        # (evaluate_events' behavior for any unmatched prediction) would
        # silently overstate the false-positive rate whenever the label
        # set is a sample rather than a full review of every firing,
        # which is the normal case for a growing dataset.
        reviewed = reviewed_predicted_frame_indices(label_data, side)
        reviewed_events = [e for e in contact_events if e.peak_frame_index in reviewed]
        predicted_by_side[side] = contact_events_to_gait_events(reviewed_events, side)

        actual, verdict_counts = labels_to_gait_events(label_data, side)
        actual_by_side[side] = actual
        verdict_summary[side] = verdict_counts
        coverage[side] = {
            "detector_events_total": len(contact_events),
            "detector_events_reviewed": len(reviewed_events),
        }

    return clip_id, predicted_by_side, actual_by_side, verdict_summary, coverage


def build_report(
    clip_id: str,
    predicted_by_side: dict[str, list[GaitEvent]],
    actual_by_side: dict[str, list[GaitEvent]],
    verdict_summary: dict[str, dict[str, int]],
    coverage: dict[str, dict[str, int]],
    tolerance_ms: int,
) -> dict:
    results_by_side = {
        side: evaluate_by_event_type(
            predicted_by_side[side], actual_by_side[side], tolerance_ms=tolerance_ms
        )
        for side in SIDES
    }

    all_predicted = [event for side in SIDES for event in predicted_by_side[side]]
    all_actual = [event for side in SIDES for event in actual_by_side[side]]
    results_combined = evaluate_by_event_type(
        all_predicted, all_actual, tolerance_ms=tolerance_ms
    )

    return {
        "schema_version": "1.0",
        "clip_id": clip_id,
        "detector": "app.services.biomechanics.contact_events (production)",
        "tolerance_ms": tolerance_ms,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "label_verdict_counts": verdict_summary,
        "review_coverage": coverage,
        "results_by_side": results_by_side,
        "results_combined": results_combined,
        "notes": [
            TOE_OFF_NOTE,
            "results are restricted to detector-fired events a human actually "
            "reviewed (see review_coverage) - an unreviewed detector firing is "
            "neither a confirmed hit nor a confirmed miss, so it is excluded "
            "from precision/recall rather than counted as an automatic false "
            "positive. Low detector_events_reviewed vs. detector_events_total "
            "means the numbers below only describe the reviewed subset, not "
            "the whole clip.",
        ],
    }


def run_single_clip(timeline_path: Path, labels_path: Path, *, tolerance_ms: int) -> dict:
    clip_id, predicted_by_side, actual_by_side, verdict_summary, coverage = collect_clip_events(
        timeline_path, labels_path
    )
    return build_report(
        clip_id, predicted_by_side, actual_by_side, verdict_summary, coverage, tolerance_ms
    )


def run_manifest(manifest_path: Path, *, tolerance_ms: int, out_dir: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_dir = manifest_path.parent

    out_dir.mkdir(parents=True, exist_ok=True)

    aggregate_predicted: list[GaitEvent] = []
    aggregate_actual: list[GaitEvent] = []
    per_clip_summary: list[dict] = []

    for clip in manifest.get("clips", []):
        clip_id = clip["clip_id"]
        labels_path = base_dir / "labels" / f"{clip_id}.json"
        if not labels_path.exists():
            print(f"skip {clip_id}: no labels file at {labels_path}")
            continue

        label_data = json.loads(labels_path.read_text(encoding="utf-8"))
        timeline_path = Path(label_data.get("source_timeline") or "")
        if not timeline_path.exists():
            print(f"skip {clip_id}: timeline not found at {timeline_path}")
            continue

        resolved_clip_id, predicted_by_side, actual_by_side, verdict_summary, coverage = collect_clip_events(
            timeline_path, labels_path
        )
        report = build_report(
            resolved_clip_id,
            predicted_by_side,
            actual_by_side,
            verdict_summary,
            coverage,
            tolerance_ms,
        )
        (out_dir / f"{resolved_clip_id}.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )

        ic = report["results_combined"]["initial_contact"]
        print(
            f"{resolved_clip_id}: precision={ic['precision']} recall={ic['recall']} "
            f"f1={ic['f1_score']}"
        )

        for side in SIDES:
            aggregate_predicted.extend(predicted_by_side[side])
            aggregate_actual.extend(actual_by_side[side])
        per_clip_summary.append({"clip_id": resolved_clip_id, "initial_contact": ic})

    aggregate = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tolerance_ms": tolerance_ms,
        "clips_included": [entry["clip_id"] for entry in per_clip_summary],
        "per_clip": per_clip_summary,
        "pooled": evaluate_by_event_type(
            aggregate_predicted, aggregate_actual, tolerance_ms=tolerance_ms
        ),
        "notes": [TOE_OFF_NOTE],
    }
    (out_dir / "_aggregate.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"\naggregate written to {out_dir / '_aggregate.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--timeline", type=Path, default=None)
    parser.add_argument("--labels", type=Path, default=None)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--tolerance-ms", type=int, default=80)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    if args.manifest:
        run_manifest(args.manifest, tolerance_ms=args.tolerance_ms, out_dir=args.out)
        return

    if not args.timeline or not args.labels:
        parser.error("either --manifest, or both --timeline and --labels, are required.")
        return

    report = run_single_clip(args.timeline, args.labels, tolerance_ms=args.tolerance_ms)

    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / f"{report['clip_id']}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    ic = report["results_combined"]["initial_contact"]
    print(f"clip_id: {report['clip_id']}")
    print(f"initial_contact (combined): precision={ic['precision']} recall={ic['recall']} f1={ic['f1_score']}")
    print(f"  timing error (ms): {ic['timing_error_ms']}")
    print(f"  counts: {ic['counts']}")
    print(f"\nfull report written to {out_path}")


if __name__ == "__main__":
    main()
