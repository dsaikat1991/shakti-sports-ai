import unittest

import numpy as np

from app.services.pose_remote.adapter import to_shakti_landmarks
from rtmpose_worker.core import (
    HALPE26_NAMES,
    RTMPoseRuntime,
    Settings,
    is_full_frame_fallback,
    normalize_bbox,
    normalize_keypoints,
)


def make_runtime_with_fake_inferencer(raw: dict) -> RTMPoseRuntime:
    settings = Settings(
        model="test-model",
        device="cpu",
        schema="halpe26",
        det_model=None,
        minimum_confidence=0.35,
        maximum_people=4,
    )
    runtime = RTMPoseRuntime(settings)
    runtime._inferencer = lambda image, return_vis, show: iter([raw])
    return runtime


def make_prediction(
    *,
    score: float,
    bbox: tuple,
    bbox_score: float,
) -> dict:
    return {
        "keypoints": [[10.0, 20.0] for _ in HALPE26_NAMES],
        "keypoint_scores": [score for _ in HALPE26_NAMES],
        "bbox": bbox,
        "bbox_score": bbox_score,
    }


class TestRTMPoseLiveIntegrationV20(unittest.TestCase):
    def test_halpe26_mapping_includes_feet(self) -> None:
        coordinates = [[i * 2.0, i * 3.0] for i in range(len(HALPE26_NAMES))]
        result = normalize_keypoints(
            coordinates=coordinates,
            scores=[0.9] * len(coordinates),
            width=200,
            height=300,
            schema_name="halpe26",
            dataset_names=None,
            minimum_confidence=0.35,
        )
        self.assertIn("left_heel", result)
        self.assertIn("right_small_toe", result)

    def test_confidence_filter(self) -> None:
        result = normalize_keypoints(
            coordinates=[[10.0, 20.0] for _ in HALPE26_NAMES],
            scores=[0.1 for _ in HALPE26_NAMES],
            width=100,
            height=100,
            schema_name="halpe26",
            dataset_names=None,
            minimum_confidence=0.35,
        )
        self.assertEqual(result, {})

    def test_adapter(self) -> None:
        response = {
            "instances": [
                {
                    "track_id": "0",
                    "confidence": 0.91,
                    "source_schema": "halpe26",
                    "bounding_box": [0, 0, 100, 200],
                    "keypoints": {
                        "left_heel": {
                            "name": "left_heel",
                            "x": 0.4,
                            "y": 0.8,
                            "confidence": 0.92,
                        }
                    },
                }
            ]
        }
        converted = to_shakti_landmarks(response)
        self.assertEqual(converted[0]["provider"], "rtmpose")
        self.assertIn("left_heel", converted[0]["landmarks"])

    def test_default_settings(self) -> None:
        settings = Settings.from_environment()
        self.assertEqual(settings.schema, "halpe26")
        self.assertTrue(settings.model)

    def test_length_validation(self) -> None:
        with self.assertRaises(ValueError):
            normalize_keypoints(
                coordinates=[[1.0, 2.0]],
                scores=[0.9, 0.8],
                width=100,
                height=100,
                schema_name="halpe26",
                dataset_names=["nose"],
                minimum_confidence=0.35,
            )

    def test_normalize_bbox_unwraps_one_item_tuple(self) -> None:
        # split_instances in MMPose 1.3.2 wraps the bbox list in a
        # one-item tuple.
        self.assertEqual(
            normalize_bbox(([1.0, 2.0, 3.0, 4.0],)),
            [1.0, 2.0, 3.0, 4.0],
        )

    def test_normalize_bbox_handles_numpy_and_invalid(self) -> None:
        self.assertEqual(
            normalize_bbox(np.array([[1.0, 2.0, 3.0, 4.0]])),
            [1.0, 2.0, 3.0, 4.0],
        )
        self.assertIsNone(normalize_bbox(None))
        self.assertIsNone(normalize_bbox([1.0, 2.0]))

    def test_full_frame_fallback_signature(self) -> None:
        self.assertTrue(
            is_full_frame_fallback(
                bbox=[0.0, 0.0, 1000.0, 300.0],
                bbox_score=1.0,
                width=1000,
                height=300,
            )
        )

    def test_real_detection_is_not_fallback(self) -> None:
        self.assertFalse(
            is_full_frame_fallback(
                bbox=[12.5, 3.2, 640.0, 298.7],
                bbox_score=0.91,
                width=1000,
                height=300,
            )
        )
        self.assertFalse(
            is_full_frame_fallback(
                bbox=[0.0, 0.0, 1000.0, 300.0],
                bbox_score=0.97,
                width=1000,
                height=300,
            )
        )

    def test_infer_reports_fallback_and_discards_garbage(self) -> None:
        raw = {
            "predictions": [
                [
                    make_prediction(
                        score=0.1,
                        bbox=([0.0, 0.0, 100.0, 50.0],),
                        bbox_score=1.0,
                    )
                ]
            ],
        }
        runtime = make_runtime_with_fake_inferencer(raw)
        result = runtime.infer(np.zeros((50, 100, 3), dtype=np.uint8))
        self.assertEqual(result["instances"], [])
        self.assertEqual(len(result["warnings"]), 2)
        self.assertIn("detector returned no boxes", result["warnings"][0])
        self.assertIn("was discarded", result["warnings"][1])

    def test_infer_keeps_real_detection_without_warnings(self) -> None:
        raw = {
            "predictions": [
                [
                    make_prediction(
                        score=0.9,
                        bbox=([5.0, 5.0, 90.0, 45.0],),
                        bbox_score=0.87,
                    )
                ]
            ],
        }
        runtime = make_runtime_with_fake_inferencer(raw)
        result = runtime.infer(np.zeros((50, 100, 3), dtype=np.uint8))
        self.assertEqual(result["warnings"], [])
        self.assertEqual(len(result["instances"]), 1)
        instance = result["instances"][0]
        self.assertFalse(instance["detector_fallback"])
        self.assertEqual(len(instance["keypoints"]), len(HALPE26_NAMES))
        self.assertEqual(instance["bounding_box"], [5.0, 5.0, 90.0, 45.0])

    def test_infer_warns_when_nothing_predicted(self) -> None:
        runtime = make_runtime_with_fake_inferencer({"predictions": []})
        result = runtime.infer(np.zeros((50, 100, 3), dtype=np.uint8))
        self.assertEqual(result["instances"], [])
        self.assertEqual(
            result["warnings"], ["No pose instance was detected."]
        )

    def test_adapter_passes_fallback_flag(self) -> None:
        converted = to_shakti_landmarks(
            {
                "instances": [
                    {
                        "track_id": "0",
                        "confidence": 0.4,
                        "source_schema": "halpe26",
                        "bounding_box": [0, 0, 100, 50],
                        "detector_fallback": True,
                        "keypoints": {},
                    }
                ]
            }
        )
        self.assertTrue(converted[0]["detector_fallback"])


if __name__ == "__main__":
    unittest.main()
