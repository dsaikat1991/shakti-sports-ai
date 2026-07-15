from __future__ import annotations

"""
Pre-labeling triage for the sprint-biomechanics research dataset (see
datasets/sprint_biomechanics/README.md for the full workflow this fits
into).

Runs the exact same tracking + quality-gate pipeline the production API
uses (app.services.pose_remote.live_analyzer.analyze_video - zero
reimplemented quality logic) and derives a verdict that answers "is this
clip labelable", not "does it pass biomechanics_ready" - those are
different questions. A bad-angle clip is still labelable (and valuable -
that's exactly the failure mode under investigation); a clip with
unreadable tracking or an invisible foot isn't labelable at all.

Requires the RTMPose worker running, same as scripts/analyze_clip.py:
    ./.venv-rtmpose/Scripts/python.exe -m uvicorn rtmpose_worker.app:app --port 8011

Usage:
    .venv/Scripts/python.exe scripts/screen_clip.py <video> \
        [--clip-id ID] [--out DIR]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.pose_remote.live_analyzer import analyze_video

DEFAULT_OUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "sprint_biomechanics"
    / "screening"
)

MIN_DETECTION_RATE_PERCENT = 60.0
MIN_FOOT_VISIBILITY_PERCENT = 30.0


def derive_screening_verdict(
    recording_quality: dict,
    detection_rate_percent: float,
) -> tuple[str, list[str]]:
    """
    Returns (verdict, reasons). verdict is one of "reject" / "marginal" /
    "accept". Pure function of already-computed quality-gate fields - no
    new tracking/quality logic, see module docstring.
    """
    reasons: list[str] = []

    body_visibility = recording_quality.get("body_visibility") or {}
    ankles = body_visibility.get("ankles")
    feet = body_visibility.get("feet")
    worst_foot_visibility = min(
        v for v in (ankles, feet) if v is not None
    ) if (ankles is not None or feet is not None) else None

    if detection_rate_percent < MIN_DETECTION_RATE_PERCENT:
        reasons.append(
            f"detection_rate_percent {detection_rate_percent:.1f}% is below "
            f"{MIN_DETECTION_RATE_PERCENT:.0f}% - tracking too unreliable to label."
        )

    if worst_foot_visibility is not None and worst_foot_visibility < MIN_FOOT_VISIBILITY_PERCENT:
        reasons.append(
            f"ankle/feet visibility {worst_foot_visibility:.1f}% is below "
            f"{MIN_FOOT_VISIBILITY_PERCENT:.0f}% - the foot isn't visible enough "
            "to judge contact vs. swing even in principle."
        )

    if reasons:
        return "reject", reasons

    biomechanics_ready = bool(recording_quality.get("biomechanics_ready", False))
    if not biomechanics_ready:
        readiness = recording_quality.get("analysis_readiness") or {}
        reasons.append(
            "fails the production biomechanics_ready gate "
            f"({readiness.get('rating', 'reason not available')}) - still "
            "labelable, and bad-angle/height footage is exactly what exposed "
            "the current ground-contact bug. Label it."
        )
        return "marginal", reasons

    reasons.append(
        "passes the full quality gate. Still worth a quick human look before "
        "investing in full labeling - the automated gate is necessary but not "
        "sufficient (occlusion/ground-texture problems aren't visible to it)."
    )
    return "accept", reasons


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Screen a candidate clip for the sprint-biomechanics research dataset."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument(
        "--clip-id",
        type=str,
        default=None,
        help="Defaults to the video's filename stem.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Directory to write the screening report to (default {DEFAULT_OUT_DIR}).",
    )
    args = parser.parse_args()

    clip_id = args.clip_id or args.video.stem

    try:
        result = analyze_video(str(args.video))
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    recording_quality = result.get("recording_quality") or {}
    detection_rate_percent = float(
        (result.get("analysis") or {}).get("detection_rate_percent") or 0.0
    )

    verdict, reasons = derive_screening_verdict(
        recording_quality, detection_rate_percent
    )

    report = {
        "schema_version": "1.0",
        "clip_id": clip_id,
        "generated_by": "scripts/screen_clip.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "verdict_reasons": reasons,
        "raw_result": result,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / f"{clip_id}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"clip_id: {clip_id}")
    print(f"verdict: {verdict.upper()}")
    for reason in reasons:
        print(f"  - {reason}")
    print(f"\nfull report written to {out_path}")


if __name__ == "__main__":
    main()
