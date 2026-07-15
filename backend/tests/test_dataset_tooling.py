"""
Pure-logic tests for the sprint-biomechanics research dataset tooling
(scripts/screen_clip.py, scripts/benchmark_contact_detector.py). These
scripts live under backend/scripts/, not the app package, and are
standalone CLI tools (same as the rest of backend/scripts/) - imported
here the same way they import `app`: by inserting their own directory
onto sys.path.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from benchmark_contact_detector import (  # noqa: E402
    contact_events_to_gait_events,
    labels_to_gait_events,
    reviewed_predicted_frame_indices,
)
from screen_clip import (  # noqa: E402
    MIN_DETECTION_RATE_PERCENT,
    MIN_FOOT_VISIBILITY_PERCENT,
    derive_screening_verdict,
)

from app.services.biomechanics.contact_events import ContactEvent  # noqa: E402


def make_contact_event(**overrides) -> ContactEvent:
    defaults = dict(
        side="right",
        contact_start_ms=1000,
        contact_end_ms=1120,
        contact_time_ms=120,
        peak_frame_index=30,
        peak_timestamp_ms=1050,
        confidence=0.8,
    )
    defaults.update(overrides)
    return ContactEvent(**defaults)


def make_recording_quality(**overrides) -> dict:
    quality = {
        "biomechanics_ready": True,
        "analysis_readiness": {"ready": True, "rating": "Excellent"},
        "body_visibility": {"ankles": 90.0, "feet": 85.0, "hips": 95.0, "knees": 92.0},
    }
    quality.update(overrides)
    return quality


class TestDeriveScreeningVerdict:
    def test_rejects_low_detection_rate(self):
        quality = make_recording_quality()
        verdict, reasons = derive_screening_verdict(
            quality, detection_rate_percent=MIN_DETECTION_RATE_PERCENT - 1
        )
        assert verdict == "reject"
        assert any("detection_rate_percent" in reason for reason in reasons)

    def test_rejects_invisible_foot(self):
        quality = make_recording_quality(
            body_visibility={"ankles": MIN_FOOT_VISIBILITY_PERCENT - 1, "feet": 20.0}
        )
        verdict, reasons = derive_screening_verdict(quality, detection_rate_percent=95.0)
        assert verdict == "reject"
        assert any("visible" in reason for reason in reasons)

    def test_marginal_when_technically_labelable_but_not_biomechanics_ready(self):
        quality = make_recording_quality(biomechanics_ready=False)
        verdict, reasons = derive_screening_verdict(quality, detection_rate_percent=95.0)
        assert verdict == "marginal"
        assert reasons

    def test_accept_when_fully_ready(self):
        quality = make_recording_quality()
        verdict, reasons = derive_screening_verdict(quality, detection_rate_percent=100.0)
        assert verdict == "accept"
        assert reasons

    def test_reject_takes_priority_over_marginal(self):
        # Fails both the hard technical bar AND biomechanics_ready - must
        # be reject, not marginal, since an invisible foot can't be
        # labeled regardless of the angle/height verdict.
        quality = make_recording_quality(
            biomechanics_ready=False,
            body_visibility={"ankles": 5.0, "feet": 5.0},
        )
        verdict, _ = derive_screening_verdict(quality, detection_rate_percent=95.0)
        assert verdict == "reject"


class TestContactEventsToGaitEvents:
    def test_converts_fields_and_event_type(self):
        events = [make_contact_event(peak_frame_index=42, peak_timestamp_ms=1400, confidence=0.6)]
        gait_events = contact_events_to_gait_events(events, side="left")

        assert len(gait_events) == 1
        event = gait_events[0]
        assert event.event_type == "initial_contact"
        assert event.side == "left"
        assert event.timestamp_ms == 1400
        assert event.frame_index == 42
        assert event.confidence == 0.6
        assert event.source == "contact_events_v1"

    def test_empty_input_gives_empty_output(self):
        assert contact_events_to_gait_events([], side="right") == []


class TestLabelsToGaitEvents:
    def test_only_true_contact_verdicts_become_gait_events(self):
        label_data = {
            "label_sets": {
                "ground_contact_peak": {
                    "sides": {
                        "right": [
                            {
                                "verdict": "true_contact",
                                "labeled_frame_index": 10,
                                "labeled_timestamp_ms": 500,
                            },
                            {"verdict": "false_positive"},
                            {"verdict": "inconclusive"},
                            {"verdict": "unusable"},
                            {
                                "verdict": "true_contact",
                                "labeled_frame_index": 40,
                                "labeled_timestamp_ms": 2100,
                            },
                        ]
                    }
                }
            }
        }

        gait_events, verdict_counts = labels_to_gait_events(label_data, side="right")

        assert [e.timestamp_ms for e in gait_events] == [500, 2100]
        assert all(e.event_type == "initial_contact" and e.source == "human_label" for e in gait_events)
        assert verdict_counts == {
            "true_contact": 2,
            "false_positive": 1,
            "inconclusive": 1,
            "unusable": 1,
        }

    def test_missing_side_returns_empty(self):
        label_data = {"label_sets": {"ground_contact_peak": {"sides": {}}}}
        gait_events, verdict_counts = labels_to_gait_events(label_data, side="left")
        assert gait_events == []
        assert verdict_counts["true_contact"] == 0

    def test_true_contact_without_timestamp_is_excluded(self):
        # A skeleton entry a reviewer marked true_contact but hasn't
        # actually filled the frame/timestamp in for yet - must not be
        # silently treated as a labeled event.
        label_data = {
            "label_sets": {
                "ground_contact_peak": {
                    "sides": {
                        "left": [
                            {"verdict": "true_contact", "labeled_timestamp_ms": None}
                        ]
                    }
                }
            }
        }
        gait_events, verdict_counts = labels_to_gait_events(label_data, side="left")
        assert gait_events == []
        assert verdict_counts["true_contact"] == 1


class TestReviewedPredictedFrameIndices:
    def test_collects_every_reviewed_peak_regardless_of_verdict(self):
        # Guards against the bug caught during the my_sprint_2.mp4 smoke
        # test: unreviewed detector firings must never be silently
        # counted as false positives just because a sparse label set
        # only reviewed a handful of the detector's total events.
        label_data = {
            "label_sets": {
                "ground_contact_peak": {
                    "sides": {
                        "right": [
                            {"detector_peak_frame_index": 21, "verdict": "true_contact"},
                            {"detector_peak_frame_index": 116, "verdict": "false_positive"},
                            {"detector_peak_frame_index": None, "verdict": "false_positive"},
                        ]
                    }
                }
            }
        }
        assert reviewed_predicted_frame_indices(label_data, side="right") == {21, 116}

    def test_missing_side_returns_empty_set(self):
        label_data = {"label_sets": {"ground_contact_peak": {"sides": {}}}}
        assert reviewed_predicted_frame_indices(label_data, side="left") == set()
