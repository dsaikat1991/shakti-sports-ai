import unittest

from app.services.reports.sprint_segment_report import (
    build_sprint_segment_report,
    build_sprint_stream_report,
    format_segment_report_text,
    format_stream_report_text,
)


def completed_segment_analysis() -> dict:
    return {
        "status": "completed",
        "reason": None,
        "frames_analyzed": 126,
        "joint_angle_summary": {
            "left_knee": {
                "coverage_percent": 96.0,
                "average_degrees": 161.2,
                "minimum_degrees": 84.0,
                "maximum_degrees": 178.4,
                "range_degrees": 94.4,
            },
            "left_hip": {
                "coverage_percent": 90.0,
                "average_degrees": 175.0,
                "minimum_degrees": 154.0,
                "maximum_degrees": 196.0,
                "range_degrees": 42.0,
            },
        },
        "knee_cycle_events": {"left": [], "right": []},
        "knee_symmetry": {"symmetry_score": 88.5},
        "cadence": {
            "status": "experimental",
            "estimated_steps_per_minute": 277.2,
            "events_used": 20,
            "method": "alternating_peak_knee_flexion_proxy",
        },
        "contact_events": {"left": [], "right": []},
        "ground_contact": {
            "status": "experimental",
            "overall": {"events": 14, "median_contact_time_ms": 80.0},
        },
        "flight_time": {
            "status": "experimental",
            "median_flight_time_ms": 128.0,
            "events_used": 8,
        },
        "duty_factor": {"duty_factor_percent": 25.0},
        "running_cycles": {
            "status": "experimental",
            "estimated_stride_frequency_hz": 2.31,
            "median_stride_duration_ms": 433.0,
            "cycles_used": 6,
        },
        "limitations": ["These outputs are not laboratory or force-plate validated."],
        "segment": {
            "start_frame_index": 100,
            "end_frame_index": 225,
            "frame_count": 126,
            "duration_ms": 2520,
        },
    }


def skipped_segment_analysis() -> dict:
    return {
        "status": "skipped",
        "reason": "Segment has 12 frames; at least 30 are needed for sprint metrics.",
        "segment": {
            "start_frame_index": 0,
            "end_frame_index": 11,
            "frame_count": 12,
            "duration_ms": 240,
        },
    }


class TestBuildSprintSegmentReport(unittest.TestCase):
    def test_completed_segment_reports_headline_metrics(self) -> None:
        report = build_sprint_segment_report(completed_segment_analysis())

        self.assertEqual(report["status"], "completed")
        self.assertEqual(report["frames_analyzed"], 126)
        self.assertEqual(report["cadence"]["steps_per_minute"], 277.2)
        self.assertEqual(report["stride"]["stride_frequency_hz"], 2.31)
        self.assertEqual(report["ground_contact"]["events"], 14)
        self.assertEqual(report["flight_time"]["median_flight_time_ms"], 128.0)
        self.assertEqual(report["duty_factor_percent"], 25.0)
        self.assertEqual(report["knee_symmetry_score"], 88.5)

    def test_completed_segment_labels_known_joint_angles(self) -> None:
        report = build_sprint_segment_report(completed_segment_analysis())

        self.assertIn("left_knee", report["joint_angles"])
        self.assertEqual(
            report["joint_angles"]["left_knee"]["label"], "Left knee angle"
        )
        self.assertEqual(
            report["joint_angles"]["left_knee"]["mean_degrees"], 161.2
        )
        # Only angles actually present in the input should appear.
        self.assertNotIn("right_knee", report["joint_angles"])

    def test_skipped_segment_carries_reason_without_crashing(self) -> None:
        report = build_sprint_segment_report(skipped_segment_analysis())

        self.assertEqual(report["status"], "skipped")
        self.assertIn("12 frames", report["reason"])
        self.assertNotIn("cadence", report)

    def test_stream_report_processes_every_segment(self) -> None:
        stream_analysis = {
            "provider": "rtmpose",
            "fps": 50.0,
            "observed_frames": 138,
            "interpolated_frames": 0,
            "unbridged_gaps": 0,
            "segments": [
                completed_segment_analysis(),
                skipped_segment_analysis(),
            ],
        }

        report = build_sprint_stream_report(stream_analysis)

        self.assertEqual(len(report["segments"]), 2)
        self.assertEqual(report["segments"][0]["status"], "completed")
        self.assertEqual(report["segments"][1]["status"], "skipped")


class TestFormatSegmentReportText(unittest.TestCase):
    def test_completed_report_text_includes_headline_lines(self) -> None:
        report = build_sprint_segment_report(completed_segment_analysis())
        text = format_segment_report_text(report, index=2)

        self.assertIn("Segment 2", text)
        self.assertIn("Frames: 126", text)
        self.assertIn("Cadence: 277.2 steps/min", text)
        self.assertIn("Ground contacts: 14", text)
        self.assertIn("Flight time: 0.128 s", text)
        self.assertIn("Left knee angle", text)
        self.assertIn("mean: 161 deg", text)

    def test_skipped_report_text_does_not_crash(self) -> None:
        report = build_sprint_segment_report(skipped_segment_analysis())
        text = format_segment_report_text(report, index=0)

        self.assertIn("Segment 0", text)
        self.assertIn("skipped", text)

    def test_stream_report_text_joins_all_segments(self) -> None:
        stream_analysis = {
            "segments": [
                completed_segment_analysis(),
                skipped_segment_analysis(),
            ],
        }
        report = build_sprint_stream_report(stream_analysis)
        text = format_stream_report_text(report)

        self.assertIn("Segment 0", text)
        self.assertIn("Segment 1", text)


if __name__ == "__main__":
    unittest.main()
