import unittest

from app.services.pose_remote.pose_stream import (
    fill_gaps,
    record_to_pose_frame,
    split_into_segments,
    timeline_to_pose_stream,
)


def make_record(
    *,
    frame_index: int,
    status: str = "tracked",
    x: float = 0.5,
    y: float = 0.5,
    confidence: float = 0.8,
    landmark_names: tuple[str, ...] = ("nose", "left_ankle"),
    fps: float = 10.0,
) -> dict:
    observed = status in {"selected", "tracked", "reselected"}
    return {
        "frame_index": frame_index,
        "timestamp_ms": round(frame_index * 1000.0 / fps),
        "tracking_status": status,
        "tracking_score": 0.9 if observed else 0.0,
        "is_observed": observed,
        "track_id": "0" if observed else None,
        "bounding_box": [10.0, 10.0, 40.0, 40.0] if observed else None,
        "landmarks": (
            {
                name: {
                    "name": name,
                    "x": x,
                    "y": y,
                    "z": None,
                    "confidence": confidence,
                }
                for name in landmark_names
            }
            if observed
            else {}
        ),
        "components": None,
        "warnings": [],
    }


def make_result(records: list[dict], *, fps: float = 10.0) -> dict:
    return {
        "video": {"fps": fps, "width": 100, "height": 50},
        "frames": records,
        "summary": {},
    }


class TestTimelineToPoseStream(unittest.TestCase):
    def test_observed_records_become_pose_frames(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="selected"),
                make_record(frame_index=1, status="tracked", x=0.6),
            ]
        )
        stream = timeline_to_pose_stream(result)

        self.assertEqual(len(stream.frames), 2)
        self.assertEqual(stream.gaps, ())
        first = stream.frames[0]
        self.assertEqual(first.backend, "rtmpose")
        self.assertEqual(first.frame_index, 0)
        self.assertEqual(first.timestamp_ms, 0)
        self.assertEqual(first.image_width, 100)
        self.assertEqual(first.image_height, 50)
        self.assertEqual(
            {keypoint.name for keypoint in first.keypoints},
            {"nose", "left_ankle"},
        )
        self.assertEqual(first.get("nose").confidence, 0.8)
        self.assertEqual(first.metadata["tracking_status"], "selected")
        self.assertEqual(first.metadata["track_id"], "0")
        self.assertEqual(stream.metadata["observed_ratio"], 1.0)

    def test_consecutive_missing_frames_collapse_into_one_gap(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="selected"),
                make_record(frame_index=1, status="coasting"),
                make_record(frame_index=2, status="lost"),
                make_record(frame_index=3, status="error"),
                make_record(frame_index=4, status="tracked"),
            ]
        )
        stream = timeline_to_pose_stream(result)

        self.assertEqual(len(stream.frames), 2)
        self.assertEqual(len(stream.gaps), 1)
        gap = stream.gaps[0]
        self.assertEqual(gap.frame_indices, (1, 2, 3))
        self.assertEqual(gap.reasons, ("coasting", "lost", "error"))
        self.assertEqual(gap.frame_count, 3)
        self.assertEqual(stream.metadata["gap_frames"], 3)
        self.assertEqual(stream.metadata["observed_ratio"], 0.4)

    def test_records_are_ordered_by_frame_index(self) -> None:
        result = make_result(
            [
                make_record(frame_index=2, status="tracked"),
                make_record(frame_index=0, status="selected"),
            ]
        )
        stream = timeline_to_pose_stream(result)
        self.assertEqual(
            [frame.frame_index for frame in stream.frames], [0, 2]
        )

    def test_empty_timeline(self) -> None:
        stream = timeline_to_pose_stream(make_result([]))
        self.assertEqual(stream.frames, ())
        self.assertEqual(stream.gaps, ())
        self.assertEqual(stream.metadata["observed_ratio"], 0.0)

    def test_missing_fps_falls_back_to_frame_indices(self) -> None:
        record = make_record(frame_index=3, status="tracked")
        record["timestamp_ms"] = None
        stream = timeline_to_pose_stream(
            {"video": {"fps": 0, "width": 100, "height": 50},
             "frames": [record]}
        )
        self.assertTrue(stream.metadata["timestamps_are_frame_indices"])
        self.assertEqual(stream.frames[0].timestamp_ms, 3)


class TestFillGaps(unittest.TestCase):
    def test_short_gap_is_interpolated(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="tracked", x=0.2, y=0.4),
                make_record(frame_index=1, status="coasting"),
                make_record(frame_index=2, status="tracked", x=0.4, y=0.8),
            ]
        )
        stream = timeline_to_pose_stream(result)
        filled = fill_gaps(stream, max_gap_ms=300)

        self.assertEqual(filled.gaps, ())
        self.assertEqual(
            [frame.frame_index for frame in filled.frames], [0, 1, 2]
        )
        middle = filled.frames[1]
        self.assertTrue(middle.metadata["interpolated"])
        self.assertEqual(middle.metadata["gap_reason"], "coasting")
        self.assertEqual(middle.metadata["source_frame_indices"], [0, 2])
        self.assertAlmostEqual(middle.get("nose").x, 0.3)
        self.assertAlmostEqual(middle.get("nose").y, 0.6)
        self.assertEqual(filled.metadata["interpolated_frames"], 1)

    def test_long_gap_is_left_untouched(self) -> None:
        records = [make_record(frame_index=0, status="tracked")]
        records += [
            make_record(frame_index=index, status="coasting")
            for index in range(1, 7)
        ]
        records.append(make_record(frame_index=7, status="tracked"))
        stream = timeline_to_pose_stream(make_result(records))

        # 700 ms between observed neighbours, cap at 300 ms.
        filled = fill_gaps(stream, max_gap_ms=300)
        self.assertEqual(len(filled.gaps), 1)
        self.assertEqual(len(filled.frames), 2)
        self.assertEqual(filled.metadata["interpolated_frames"], 0)

    def test_gap_at_stream_start_is_not_filled(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="lost"),
                make_record(frame_index=1, status="selected"),
            ]
        )
        filled = fill_gaps(
            timeline_to_pose_stream(result), max_gap_ms=1000
        )
        self.assertEqual(len(filled.gaps), 1)

    def test_only_shared_landmarks_are_interpolated(self) -> None:
        result = make_result(
            [
                make_record(
                    frame_index=0,
                    status="tracked",
                    landmark_names=("nose", "left_ankle"),
                ),
                make_record(frame_index=1, status="coasting"),
                make_record(
                    frame_index=2,
                    status="tracked",
                    landmark_names=("nose", "right_ankle"),
                ),
            ]
        )
        filled = fill_gaps(
            timeline_to_pose_stream(result), max_gap_ms=300
        )
        middle = filled.frames[1]
        self.assertEqual(
            [keypoint.name for keypoint in middle.keypoints], ["nose"]
        )

    def test_interpolated_confidence_is_conservative(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="tracked", confidence=0.9),
                make_record(frame_index=1, status="coasting"),
                make_record(frame_index=2, status="tracked", confidence=0.5),
            ]
        )
        filled = fill_gaps(
            timeline_to_pose_stream(result), max_gap_ms=300
        )
        self.assertEqual(filled.frames[1].get("nose").confidence, 0.5)

    def test_multiple_gaps_filled_independently(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="tracked", x=0.2),
                make_record(frame_index=1, status="coasting"),
                make_record(frame_index=2, status="tracked", x=0.4),
                make_record(frame_index=3, status="error"),
                make_record(frame_index=4, status="tracked", x=0.6),
            ]
        )
        filled = fill_gaps(
            timeline_to_pose_stream(result), max_gap_ms=300
        )
        self.assertEqual(filled.gaps, ())
        self.assertEqual(len(filled.frames), 5)
        self.assertEqual(filled.metadata["interpolated_frames"], 2)
        self.assertAlmostEqual(filled.frames[1].get("nose").x, 0.3)
        self.assertAlmostEqual(filled.frames[3].get("nose").x, 0.5)


class TestSplitIntoSegments(unittest.TestCase):
    def make_stream_with_cut(self):
        # Observed 0-2, a long unfillable gap 3-9 (editing cut),
        # observed 10-12.
        records = [
            make_record(frame_index=index, status="tracked")
            for index in range(3)
        ]
        records += [
            make_record(frame_index=index, status="coasting")
            for index in range(3, 10)
        ]
        records += [
            make_record(frame_index=index, status="tracked")
            for index in range(10, 13)
        ]
        return timeline_to_pose_stream(make_result(records))

    def test_unfilled_gap_becomes_segment_boundary(self) -> None:
        stream = self.make_stream_with_cut()
        filled = fill_gaps(stream, max_gap_ms=300)
        self.assertEqual(len(filled.gaps), 1)

        segments = split_into_segments(filled)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].start_frame_index, 0)
        self.assertEqual(segments[0].end_frame_index, 2)
        self.assertEqual(segments[1].start_frame_index, 10)
        self.assertEqual(segments[1].end_frame_index, 12)
        self.assertEqual(segments[0].duration_ms, 200)

    def test_filled_gaps_do_not_split(self) -> None:
        result = make_result(
            [
                make_record(frame_index=0, status="tracked"),
                make_record(frame_index=1, status="coasting"),
                make_record(frame_index=2, status="tracked"),
            ]
        )
        filled = fill_gaps(
            timeline_to_pose_stream(result), max_gap_ms=300
        )
        segments = split_into_segments(filled)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].frame_count, 3)

    def test_minimum_frames_drops_stubs(self) -> None:
        stream = self.make_stream_with_cut()
        filled = fill_gaps(stream, max_gap_ms=300)
        segments = split_into_segments(filled, minimum_frames=4)
        self.assertEqual(segments, ())

    def test_empty_stream(self) -> None:
        stream = timeline_to_pose_stream(make_result([]))
        self.assertEqual(split_into_segments(stream), ())

    def test_split_without_fill_uses_all_gaps(self) -> None:
        stream = self.make_stream_with_cut()
        segments = split_into_segments(stream)
        self.assertEqual(len(segments), 2)


class TestRecordToPoseFrame(unittest.TestCase):
    def test_z_is_carried_when_present(self) -> None:
        record = make_record(frame_index=0, status="tracked")
        record["landmarks"]["nose"]["z"] = 0.12
        frame = record_to_pose_frame(
            record, image_width=100, image_height=50
        )
        self.assertAlmostEqual(frame.get("nose").z, 0.12)
        self.assertIsNone(frame.get("left_ankle").z)


if __name__ == "__main__":
    unittest.main()
