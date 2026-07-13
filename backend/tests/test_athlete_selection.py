import unittest

from app.services.pose_remote.athlete_selection import (
    AthleteTracker,
    SelectionWeights,
    bbox_iou,
    landmark_similarity,
    match_score,
    select_primary_athlete,
    selection_score,
    TrackerWeights,
)

FRAME_WIDTH = 1000
FRAME_HEIGHT = 600


def make_instance(
    *,
    track_id: str,
    bbox: list[float],
    confidence: float = 0.8,
    keypoint_count: int = 26,
    detector_fallback: bool = False,
) -> dict:
    centre_x = (bbox[0] + bbox[2]) / 2.0 / FRAME_WIDTH
    centre_y = (bbox[1] + bbox[3]) / 2.0 / FRAME_HEIGHT
    keypoints = {
        f"kp{i}": {
            "name": f"kp{i}",
            "x": centre_x,
            "y": centre_y,
            "confidence": confidence,
        }
        for i in range(keypoint_count)
    }
    return {
        "track_id": track_id,
        "bounding_box": bbox,
        "confidence": confidence,
        "source_schema": "halpe26",
        "detector_fallback": detector_fallback,
        "keypoints": keypoints,
    }


class TestPrimaryAthleteSelector(unittest.TestCase):
    def test_largest_central_athlete_wins(self) -> None:
        background_runner = make_instance(
            track_id="0", bbox=[20.0, 20.0, 120.0, 220.0]
        )
        main_athlete = make_instance(
            track_id="1", bbox=[350.0, 100.0, 650.0, 550.0]
        )
        result = select_primary_athlete(
            [background_runner, main_athlete],
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
        )
        self.assertEqual(result.reason, "scored")
        self.assertEqual(result.instance["track_id"], "1")

    def test_manual_override_wins(self) -> None:
        background_runner = make_instance(
            track_id="0", bbox=[20.0, 20.0, 120.0, 220.0]
        )
        main_athlete = make_instance(
            track_id="1", bbox=[350.0, 100.0, 650.0, 550.0]
        )
        result = select_primary_athlete(
            [background_runner, main_athlete],
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            override_track_id="0",
        )
        self.assertEqual(result.reason, "manual_override")
        self.assertEqual(result.instance["track_id"], "0")

    def test_fallback_instance_loses_to_real_detection(self) -> None:
        fallback = make_instance(
            track_id="0",
            bbox=[0.0, 0.0, float(FRAME_WIDTH), float(FRAME_HEIGHT)],
            detector_fallback=True,
        )
        real = make_instance(track_id="1", bbox=[50.0, 50.0, 250.0, 400.0])
        result = select_primary_athlete(
            [fallback, real], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertEqual(result.instance["track_id"], "1")

    def test_lone_fallback_instance_is_still_used(self) -> None:
        fallback = make_instance(
            track_id="0",
            bbox=[0.0, 0.0, float(FRAME_WIDTH), float(FRAME_HEIGHT)],
            detector_fallback=True,
        )
        result = select_primary_athlete(
            [fallback], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertEqual(result.instance["track_id"], "0")

    def test_region_of_interest_prefers_athlete_inside(self) -> None:
        outside_lane = make_instance(
            track_id="0", bbox=[300.0, 50.0, 700.0, 550.0]
        )
        in_lane = make_instance(
            track_id="1", bbox=[820.0, 200.0, 980.0, 500.0]
        )
        result = select_primary_athlete(
            [outside_lane, in_lane],
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            region_of_interest=[800.0, 0.0, 1000.0, 600.0],
        )
        self.assertEqual(result.instance["track_id"], "1")

    def test_empty_frame_returns_none(self) -> None:
        result = select_primary_athlete(
            [], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertIsNone(result.instance)
        self.assertEqual(result.reason, "none_available")

    def test_confidence_breaks_equal_geometry(self) -> None:
        bbox = [400.0, 200.0, 600.0, 400.0]
        low = make_instance(track_id="0", bbox=bbox, confidence=0.4)
        high = make_instance(track_id="1", bbox=bbox, confidence=0.9)
        result = select_primary_athlete(
            [low, high], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertEqual(result.instance["track_id"], "1")

    def test_score_is_normalized(self) -> None:
        instance = make_instance(
            track_id="0", bbox=[0.0, 0.0, float(FRAME_WIDTH), float(FRAME_HEIGHT)]
        )
        score = selection_score(
            instance,
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            weights=SelectionWeights(),
        )
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestGeometry(unittest.TestCase):
    def test_bbox_iou(self) -> None:
        box = [0.0, 0.0, 100.0, 100.0]
        self.assertAlmostEqual(bbox_iou(box, box), 1.0)
        self.assertEqual(
            bbox_iou(box, [200.0, 200.0, 300.0, 300.0]), 0.0
        )
        self.assertAlmostEqual(
            bbox_iou(box, [50.0, 0.0, 150.0, 100.0]), 1.0 / 3.0
        )

    def test_landmark_similarity_identical_and_distant(self) -> None:
        near_a = make_instance(track_id="0", bbox=[100.0, 100.0, 200.0, 300.0])
        near_b = make_instance(track_id="1", bbox=[110.0, 100.0, 210.0, 300.0])
        far = make_instance(track_id="2", bbox=[800.0, 300.0, 950.0, 550.0])
        self.assertAlmostEqual(landmark_similarity(near_a, near_a), 1.0)
        self.assertGreater(
            landmark_similarity(near_a, near_b),
            landmark_similarity(near_a, far),
        )


class TestAthleteTracker(unittest.TestCase):
    def test_first_frame_selects_primary(self) -> None:
        tracker = AthleteTracker(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        athlete = make_instance(track_id="0", bbox=[350.0, 100.0, 650.0, 550.0])
        result = tracker.update([athlete], frame_index=0)
        self.assertEqual(result.reason, "selected")
        self.assertEqual(result.instance["track_id"], "0")

    def test_continuity_beats_a_larger_newcomer(self) -> None:
        tracker = AthleteTracker(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        athlete_f1 = make_instance(
            track_id="0", bbox=[100.0, 150.0, 300.0, 500.0]
        )
        tracker.update([athlete_f1], frame_index=0)

        # Same athlete moved slightly right; a larger, more central person
        # enters the frame. The selector alone would pick the newcomer.
        athlete_f2 = make_instance(
            track_id="0", bbox=[130.0, 150.0, 330.0, 500.0]
        )
        newcomer = make_instance(
            track_id="1", bbox=[350.0, 80.0, 700.0, 580.0]
        )
        selector_choice = select_primary_athlete(
            [athlete_f2, newcomer], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertEqual(selector_choice.instance["track_id"], "1")

        tracked = tracker.update([athlete_f2, newcomer], frame_index=1)
        self.assertEqual(tracked.reason, "tracked")
        self.assertEqual(tracked.instance["track_id"], "0")

    def test_coasting_then_reselect(self) -> None:
        tracker = AthleteTracker(
            width=FRAME_WIDTH, height=FRAME_HEIGHT, maximum_missed_frames=1
        )
        athlete = make_instance(track_id="0", bbox=[100.0, 150.0, 300.0, 500.0])
        tracker.update([athlete], frame_index=0)

        coasting = tracker.update([], frame_index=1)
        self.assertEqual(coasting.reason, "coasting")
        self.assertEqual(coasting.instance["track_id"], "0")

        replacement = make_instance(
            track_id="9", bbox=[700.0, 100.0, 950.0, 550.0]
        )
        reselected = tracker.update([replacement], frame_index=2)
        self.assertEqual(reselected.reason, "reselected")
        self.assertEqual(reselected.instance["track_id"], "9")
        self.assertTrue(reselected.is_observed)

    def test_lost_when_nothing_to_reselect(self) -> None:
        tracker = AthleteTracker(
            width=FRAME_WIDTH, height=FRAME_HEIGHT, maximum_missed_frames=0
        )
        athlete = make_instance(track_id="0", bbox=[100.0, 150.0, 300.0, 500.0])
        tracker.update([athlete], frame_index=0)
        lost = tracker.update([], frame_index=1)
        self.assertIsNone(lost.instance)
        self.assertEqual(lost.reason, "lost")

    def test_force_target_manual_override(self) -> None:
        tracker = AthleteTracker(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        main = make_instance(track_id="0", bbox=[350.0, 100.0, 650.0, 550.0])
        rival = make_instance(track_id="1", bbox=[50.0, 200.0, 180.0, 450.0])
        tracker.update([main, rival], frame_index=0)

        tracker.force_target(rival)
        rival_moved = make_instance(
            track_id="1", bbox=[60.0, 200.0, 190.0, 450.0]
        )
        tracked = tracker.update([main, rival_moved], frame_index=1)
        self.assertEqual(tracked.instance["track_id"], "1")

    def test_match_score_prefers_same_athlete(self) -> None:
        target = make_instance(track_id="0", bbox=[100.0, 150.0, 300.0, 500.0])
        same = make_instance(track_id="0", bbox=[120.0, 150.0, 320.0, 500.0])
        other = make_instance(track_id="1", bbox=[700.0, 100.0, 950.0, 550.0])
        same_score = match_score(
            same,
            target,
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            weights=TrackerWeights(),
        )
        other_score = match_score(
            other,
            target,
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            weights=TrackerWeights(),
        )
        self.assertGreater(same_score, 0.5)
        self.assertLess(other_score, same_score)

    def test_update_from_response(self) -> None:
        tracker = AthleteTracker(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        response = {
            "instances": [
                make_instance(track_id="0", bbox=[350.0, 100.0, 650.0, 550.0])
            ],
        }
        result = tracker.update_from_response(response, frame_index=0)
        self.assertEqual(result.instance["track_id"], "0")

    def test_update_from_response_adopts_frame_dimensions(self) -> None:
        tracker = AthleteTracker(width=0, height=0)
        response = {
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
            "instances": [
                make_instance(track_id="0", bbox=[350.0, 100.0, 650.0, 550.0])
            ],
        }
        tracker.update_from_response(response, frame_index=0)
        self.assertEqual(tracker.width, FRAME_WIDTH)
        self.assertEqual(tracker.height, FRAME_HEIGHT)

    def test_is_observed_classification(self) -> None:
        tracker = AthleteTracker(
            width=FRAME_WIDTH, height=FRAME_HEIGHT, maximum_missed_frames=1
        )
        athlete = make_instance(track_id="0", bbox=[100.0, 150.0, 300.0, 500.0])

        selected = tracker.update([athlete], frame_index=0)
        self.assertTrue(selected.is_observed)

        tracked = tracker.update([athlete], frame_index=1)
        self.assertTrue(tracked.is_observed)

        coasting = tracker.update([], frame_index=2)
        self.assertEqual(coasting.reason, "coasting")
        self.assertFalse(coasting.is_observed)

        # Reappearing within the miss budget is recovered by matching,
        # not by re-selection.
        recovered = tracker.update([athlete], frame_index=3)
        self.assertEqual(recovered.reason, "tracked")
        self.assertTrue(recovered.is_observed)

        tracker.update([], frame_index=4)
        lost = tracker.update([], frame_index=5)
        self.assertEqual(lost.reason, "lost")
        self.assertFalse(lost.is_observed)

        selected_again = tracker.update([athlete], frame_index=6)
        self.assertEqual(selected_again.reason, "selected")
        self.assertTrue(selected_again.is_observed)

    def test_tracked_selection_exposes_match_components(self) -> None:
        tracker = AthleteTracker(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        athlete = make_instance(track_id="0", bbox=[100.0, 150.0, 300.0, 500.0])
        tracker.update([athlete], frame_index=0)
        tracked = tracker.update([athlete], frame_index=1)
        self.assertEqual(tracked.reason, "tracked")
        for key in (
            "bbox_overlap_score",
            "centre_motion_score",
            "size_similarity_score",
            "landmark_similarity_score",
            "track_id_score",
            "final_score",
        ):
            self.assertIn(key, tracked.components)
        self.assertAlmostEqual(
            tracked.components["final_score"], tracked.score
        )


class TestComponentScores(unittest.TestCase):
    def test_selection_result_exposes_components(self) -> None:
        small = make_instance(track_id="0", bbox=[20.0, 20.0, 120.0, 220.0])
        large = make_instance(track_id="1", bbox=[350.0, 100.0, 650.0, 550.0])
        result = select_primary_athlete(
            [small, large], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertEqual(result.selected_index, 1)
        self.assertEqual(
            len(result.candidate_components), len(result.candidate_scores)
        )
        for key in (
            "bbox_area_score",
            "centre_score",
            "confidence_score",
            "completeness_score",
            "final_score",
        ):
            self.assertIn(key, result.components)
        self.assertAlmostEqual(result.components["final_score"], result.score)

    def test_selected_index_refers_to_input_order(self) -> None:
        fallback = make_instance(
            track_id="0",
            bbox=[0.0, 0.0, float(FRAME_WIDTH), float(FRAME_HEIGHT)],
            detector_fallback=True,
        )
        real = make_instance(track_id="1", bbox=[50.0, 50.0, 250.0, 400.0])
        result = select_primary_athlete(
            [fallback, real], width=FRAME_WIDTH, height=FRAME_HEIGHT
        )
        self.assertEqual(result.selected_index, 1)
        self.assertEqual(result.instance["track_id"], "1")


if __name__ == "__main__":
    unittest.main()
