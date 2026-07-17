"""Generates known-answer fixtures from the real Python digital_twin /
digital_twin_v2 functions, for the TypeScript Digital Twin engine's
parity tests to check against (frontend/src/features/performances/lib/
twinEngine.parity.test.ts).

This is a one-off developer tool, not part of any live pipeline - run it
by hand whenever the fixture set needs regenerating (e.g. if new
scenarios are added), same pattern as scripts/analyze_clip.py etc.

Run: cd backend && ./.venv/Scripts/python.exe scripts/generate_twin_parity_fixtures.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.digital_twin.models import AthleteMetricSnapshot
from app.services.digital_twin.personal_bests import find_personal_best
from app.services.digital_twin_v2.models import TwinSession
from app.services.digital_twin_v2.trends import analyze_longitudinal_trends

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "src"
    / "features"
    / "performances"
    / "lib"
    / "__fixtures__"
    / "twinParity.fixtures.json"
)

# Each scenario: a plain list of (recorded_at, value) pairs for one
# metric, run through both analyze_longitudinal_trends (trend fixture)
# and find_personal_best (personal-best fixture). Chosen to exercise
# every branch of both functions: too few samples, exactly 2, exactly 3,
# a clean improving/regressing/stable run, and a genuinely noisy
# (high-variability) run.
SCENARIOS = {
    "single_sample": [
        ("2026-01-10", 180.0),
    ],
    "two_samples_improving": [
        ("2026-01-10", 180.0),
        ("2026-03-15", 188.0),
    ],
    "two_samples_stable": [
        ("2026-01-10", 180.0),
        ("2026-03-15", 180.2),
    ],
    "three_samples_improving": [
        ("2026-01-10", 180.0),
        ("2026-03-15", 186.0),
        ("2026-06-02", 191.0),
    ],
    "three_samples_regressing": [
        ("2026-01-10", 191.0),
        ("2026-03-15", 186.0),
        ("2026-06-02", 180.0),
    ],
    "three_samples_stable": [
        ("2026-01-10", 185.0),
        ("2026-03-15", 185.4),
        ("2026-06-02", 184.8),
    ],
    "five_samples_high_variability": [
        ("2026-01-10", 150.0),
        ("2026-03-15", 220.0),
        ("2026-06-02", 140.0),
        ("2026-08-20", 215.0),
        ("2026-11-05", 155.0),
    ],
    "five_samples_gradual_improvement": [
        ("2026-01-10", 178.0),
        ("2026-03-15", 181.0),
        ("2026-06-02", 184.0),
        ("2026-08-20", 187.0),
        ("2026-11-05", 189.0),
    ],
}


def build_trend_fixture(name: str, points: list[tuple[str, float]]) -> dict:
    sessions = [
        TwinSession(
            athlete_id="fixture-athlete",
            performance_id=f"perf-{i}",
            session_id=None,
            event="Sprint",
            recorded_at=recorded_at,
            features={"metric": value},
        )
        for i, (recorded_at, value) in enumerate(points)
    ]

    # Run at minimum_samples=1 so every scenario (including the single-
    # sample one) produces a result to snapshot, even though the
    # TypeScript port applies its own, different minimum (2) - the
    # fixture captures what the Python function computes at every
    # sample count; the TS test decides which rows it's allowed to
    # compare against given its own documented minimum.
    result = analyze_longitudinal_trends(sessions, minimum_samples=1)

    return {
        "scenario": name,
        "input": {"points": [{"recorded_at": r, "value": v} for r, v in points]},
        "python_output": result["trends"].get("metric"),
    }


def build_personal_best_fixture(name: str, points: list[tuple[str, float]]) -> dict:
    snapshots = [
        AthleteMetricSnapshot(
            athlete_id="fixture-athlete",
            performance_id=f"perf-{i}",
            session_id=None,
            event="Sprint",
            recorded_at=recorded_at,
            metrics={"metric": value},
        )
        for i, (recorded_at, value) in enumerate(points)
    ]

    result_max = find_personal_best(snapshots, metric_name="metric", lower_is_better=False)
    result_min = find_personal_best(snapshots, metric_name="metric", lower_is_better=True)

    return {
        "scenario": name,
        "input": {"points": [{"recorded_at": r, "value": v} for r, v in points]},
        "python_output_higher_is_better": result_max["personal_best"],
        "python_output_lower_is_better": result_min["personal_best"],
    }


def main() -> None:
    fixtures = {
        "trend": [build_trend_fixture(name, points) for name, points in SCENARIOS.items()],
        "personal_best": [
            build_personal_best_fixture(name, points) for name, points in SCENARIOS.items()
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(fixtures, indent=2))
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
