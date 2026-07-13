import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from app.services.pose_remote.athlete_selection import AthleteTracker
from app.services.pose_remote.video_pipeline import analyze_video_with_tracking

FRAME_WIDTH = 64
FRAME_HEIGHT = 48


def write_test_video(path: Path, *, frame_count: int) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        10.0,
        (FRAME_WIDTH, FRAME_HEIGHT),
    )
    if not writer.isOpened():
        raise RuntimeError("Could not open test video writer.")
    for index in range(frame_count):
        frame = np.full(
            (FRAME_HEIGHT, FRAME_WIDTH, 3), (index * 20) % 255, dtype=np.uint8
        )
        writer.write(frame)
    writer.release()


def make_response(*, with_person: bool, bbox: list[float] | None = None) -> dict:
    instances = []
    warnings = []
    if with_person:
        bbox = bbox or [10.0, 10.0, 40.0, 40.0]
        centre_x = (bbox[0] + bbox[2]) / 2.0 / FRAME_WIDTH
        centre_y = (bbox[1] + bbox[3]) / 2.0 / FRAME_HEIGHT
        instances.append(
            {
                "track_id": "0",
                "bounding_box": bbox,
                "confidence": 0.8,
                "source_schema": "halpe26",
                "detector_fallback": False,
                "keypoints": {
                    f"kp{i}": {
                        "name": f"kp{i}",
                        "x": centre_x,
                        "y": centre_y,
                        "confidence": 0.8,
                    }
                    for i in range(26)
                },
            }
        )
    else:
        warnings.append("No pose instance was detected.")
    return {
        "status": "completed",
        "width": FRAME_WIDTH,
        "height": FRAME_HEIGHT,
        "instances": instances,
        "warnings": warnings,
    }


class FakeWorker:
    def __init__(self, responses: list) -> None:
        self.responses = list(responses)
        self.calls = 0

    def infer_image_bytes(self, *, content: bytes, filename: str = "frame.jpg") -> dict:
        index = min(self.calls, len(self.responses) - 1)
        self.calls += 1
        response = self.responses[index]
        if isinstance(response, Exception):
            raise response
        return response


class TestVideoPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self.video_path = Path(self._tempdir.name) / "clip.avi"

    def test_timeline_statuses_and_records(self) -> None:
        write_test_video(self.video_path, frame_count=4)
        worker = FakeWorker(
            [
                make_response(with_person=True),
                make_response(with_person=True, bbox=[12.0, 10.0, 42.0, 40.0]),
                make_response(with_person=False),
                make_response(with_person=True, bbox=[14.0, 10.0, 44.0, 40.0]),
            ]
        )
        result = analyze_video_with_tracking(self.video_path, worker=worker)

        statuses = [record["tracking_status"] for record in result["frames"]]
        self.assertEqual(
            statuses, ["selected", "tracked", "coasting", "tracked"]
        )
        observed = [record["is_observed"] for record in result["frames"]]
        self.assertEqual(observed, [True, True, False, True])

        first = result["frames"][0]
        for key in (
            "frame_index",
            "timestamp_ms",
            "tracking_status",
            "tracking_score",
            "is_observed",
            "track_id",
            "bounding_box",
            "landmarks",
            "components",
            "warnings",
        ):
            self.assertIn(key, first)
        self.assertEqual(first["timestamp_ms"], 0)
        self.assertEqual(result["frames"][1]["timestamp_ms"], 100)
        self.assertEqual(len(first["landmarks"]), 26)

        # The coasting frame repeats the last confirmed pose but is
        # explicitly not an observation.
        coasting = result["frames"][2]
        self.assertEqual(coasting["track_id"], "0")
        self.assertFalse(coasting["is_observed"])

        self.assertEqual(result["summary"]["observed_frames"], 3)
        self.assertEqual(
            result["summary"]["status_counts"],
            {"selected": 1, "tracked": 2, "coasting": 1},
        )

    def test_frame_stride_samples_subset(self) -> None:
        write_test_video(self.video_path, frame_count=8)
        worker = FakeWorker([make_response(with_person=True)])
        result = analyze_video_with_tracking(
            self.video_path, worker=worker, frame_stride=2
        )
        self.assertEqual(
            [record["frame_index"] for record in result["frames"]],
            [0, 2, 4, 6],
        )
        self.assertEqual(result["video"]["sampled_frames"], 4)

    def test_max_frames_limits_processing(self) -> None:
        write_test_video(self.video_path, frame_count=8)
        worker = FakeWorker([make_response(with_person=True)])
        result = analyze_video_with_tracking(
            self.video_path, worker=worker, max_frames=2
        )
        self.assertEqual(len(result["frames"]), 2)

    def test_tracker_adopts_response_dimensions(self) -> None:
        write_test_video(self.video_path, frame_count=2)
        worker = FakeWorker([make_response(with_person=True)])
        tracker = AthleteTracker(width=0, height=0)
        analyze_video_with_tracking(
            self.video_path, worker=worker, tracker=tracker
        )
        self.assertEqual(tracker.width, FRAME_WIDTH)
        self.assertEqual(tracker.height, FRAME_HEIGHT)

    def test_single_error_is_recorded_and_processing_continues(self) -> None:
        write_test_video(self.video_path, frame_count=3)
        worker = FakeWorker(
            [
                make_response(with_person=True),
                RuntimeError("worker unavailable"),
                make_response(with_person=True),
            ]
        )
        result = analyze_video_with_tracking(self.video_path, worker=worker)
        statuses = [record["tracking_status"] for record in result["frames"]]
        self.assertEqual(statuses, ["selected", "error", "tracked"])
        self.assertFalse(result["frames"][1]["is_observed"])
        self.assertIn(
            "worker unavailable", result["frames"][1]["warnings"][0]
        )

    def test_aborts_after_persistent_worker_failure(self) -> None:
        write_test_video(self.video_path, frame_count=10)
        worker = FakeWorker([RuntimeError("worker down")])
        with self.assertRaises(RuntimeError):
            analyze_video_with_tracking(self.video_path, worker=worker)

    def test_unreadable_video_raises(self) -> None:
        with self.assertRaises(ValueError):
            analyze_video_with_tracking(
                Path(self._tempdir.name) / "missing.avi",
                worker=FakeWorker([make_response(with_person=True)]),
            )


if __name__ == "__main__":
    unittest.main()
