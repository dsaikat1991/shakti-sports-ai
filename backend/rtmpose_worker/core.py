from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import cv2
import numpy as np

HALPE26_NAMES = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
    "head", "neck", "hip", "left_big_toe", "right_big_toe",
    "left_small_toe", "right_small_toe", "left_heel", "right_heel",
)

COCO17_NAMES = HALPE26_NAMES[:17]


@dataclass(slots=True, frozen=True)
class Settings:
    model: str
    device: str
    schema: str
    det_model: str | None
    minimum_confidence: float
    maximum_people: int

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            model=os.getenv(
                "RTMPOSE_MODEL",
                "rtmpose-t_8xb1024-700e_body8-halpe26-256x192",
            ),
            device=os.getenv("RTMPOSE_DEVICE", "cuda:0"),
            schema=os.getenv("RTMPOSE_SCHEMA", "halpe26"),
            det_model=os.getenv("RTMPOSE_DET_MODEL"),
            minimum_confidence=float(
                os.getenv("RTMPOSE_MIN_CONFIDENCE", "0.35")
            ),
            maximum_people=int(os.getenv("RTMPOSE_MAX_PEOPLE", "4")),
        )


def schema_names(schema_name: str) -> tuple[str, ...]:
    normalized = schema_name.lower()
    if normalized in {"halpe26", "halpe_26"}:
        return HALPE26_NAMES
    if normalized in {"coco17", "coco", "coco_17"}:
        return COCO17_NAMES
    raise ValueError(f"Unsupported keypoint schema: {schema_name}")


def normalize_keypoints(
    *,
    coordinates: list[list[float]],
    scores: list[float],
    width: int,
    height: int,
    schema_name: str,
    dataset_names: list[str] | None,
    minimum_confidence: float,
) -> dict[str, dict[str, float | str | None]]:
    names = tuple(dataset_names) if dataset_names else schema_names(schema_name)
    if not (len(names) == len(coordinates) == len(scores)):
        raise ValueError("Names, coordinates and scores must have equal lengths.")

    result: dict[str, dict[str, float | str | None]] = {}
    for name, point, score in zip(names, coordinates, scores, strict=True):
        confidence = float(score)
        if confidence < minimum_confidence or len(point) < 2:
            continue
        result[str(name)] = {
            "name": str(name),
            "x": float(point[0]) / max(width, 1),
            "y": float(point[1]) / max(height, 1),
            "z": float(point[2]) if len(point) > 2 else None,
            "confidence": confidence,
        }
    return result

def normalize_bbox(bbox: Any) -> list[float] | None:
    # MMPose 1.3.2 may return bbox as a NumPy array, a flat list,
    # a nested list, or a one-item tuple containing the coordinates.
    if hasattr(bbox, "tolist"):
        bbox = bbox.tolist()

    while (
        isinstance(bbox, (list, tuple))
        and len(bbox) == 1
        and isinstance(bbox[0], (list, tuple, np.ndarray))
    ):
        bbox = bbox[0]
        if hasattr(bbox, "tolist"):
            bbox = bbox.tolist()

    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        try:
            return [float(value) for value in bbox[:4]]
        except (TypeError, ValueError):
            return None
    return None


def is_full_frame_fallback(
    *,
    bbox: list[float] | None,
    bbox_score: Any,
    width: int,
    height: int,
) -> bool:
    # When the detector returns no person boxes, MMPose's top-down
    # inferencer substitutes the whole image as the bbox with a synthetic
    # score of exactly 1.0. Treat that signature as "no detection" instead
    # of a real person.
    if bbox != [0.0, 0.0, float(width), float(height)]:
        return False
    if bbox_score is None:
        return True
    try:
        return float(bbox_score) >= 0.9999
    except (TypeError, ValueError):
        return True


def make_json_safe(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ) or value is None:
        return value

    return repr(value)


def dump_raw_prediction(
    raw: dict[str, Any],
) -> None:
    if os.getenv(
        "RTMPOSE_DEBUG_RAW",
        "false",
    ).lower() not in {
        "1",
        "true",
        "yes",
    }:
        return

    output_path = Path(
        os.getenv(
            "RTMPOSE_DEBUG_PATH",
            "temp/rtmpose_raw_prediction.json",
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            make_json_safe(raw),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"RTMPose raw prediction saved to: "
        f"{output_path.resolve()}"
    )



class RTMPoseRuntime:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._inferencer = None
        self.initialization_error: str | None = None

    @property
    def initialized(self) -> bool:
        return self._inferencer is not None

    def initialize(self) -> None:
        if self._inferencer is not None:
            return
        try:
            from mmpose.apis import MMPoseInferencer

            kwargs: dict[str, Any] = {
                "pose2d": self.settings.model,
                "device": self.settings.device,
            }
            if self.settings.det_model:
                kwargs["det_model"] = self.settings.det_model
            self._inferencer = MMPoseInferencer(**kwargs)
            self.initialization_error = None
        except Exception as exc:
            self.initialization_error = str(exc)
            raise RuntimeError(
                "RTMPose initialization failed. Verify model/config, checkpoint, "
                "detector and CUDA device."
            ) from exc

    @staticmethod
    def decode_image(content: bytes) -> np.ndarray:
        image = cv2.imdecode(
            np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if image is None:
            raise ValueError("The uploaded file is not a decodable image.")
        return image

    def infer(self, image: np.ndarray) -> dict[str, Any]:
        self.initialize()
        height, width = image.shape[:2]
        started = perf_counter()
        raw = next(self._inferencer(image, return_vis=False, show=False))
        dump_raw_prediction(raw)
        inference_ms = (perf_counter() - started) * 1000.0
        predictions = raw.get("predictions", [])
        if predictions and isinstance(predictions[0], list):
            predictions = predictions[0]

        instances = []
        warnings: list[str] = []
        for index, prediction in enumerate(
            predictions[: self.settings.maximum_people]
        ):
            coordinates = prediction.get("keypoints", [])
            scores = prediction.get(
                "keypoint_scores", prediction.get("keypoints_visible", [])
            )
            keypoints = normalize_keypoints(
                coordinates=coordinates,
                scores=scores,
                width=width,
                height=height,
                schema_name=self.settings.schema,
                dataset_names=prediction.get("keypoint_names"),
                minimum_confidence=self.settings.minimum_confidence,
            )
            confidence = (
                sum(float(item["confidence"]) for item in keypoints.values())
                / len(keypoints)
                if keypoints
                else 0.0
            )
            normalized_bbox = normalize_bbox(prediction.get("bbox"))
            detector_fallback = is_full_frame_fallback(
                bbox=normalized_bbox,
                bbox_score=prediction.get("bbox_score"),
                width=width,
                height=height,
            )

            if detector_fallback:
                warnings.append(
                    "The person detector returned no boxes; pose was "
                    "estimated on the full frame as a fallback."
                )

            if not keypoints:
                warnings.append(
                    f"Instance {index} was discarded: all "
                    f"{len(coordinates)} keypoints were below the minimum "
                    f"confidence {self.settings.minimum_confidence}."
                )
                continue

            instances.append(
                {
                    "track_id": str(prediction.get("track_id", index)),
                    "bounding_box": normalized_bbox,
                    "confidence": confidence,
                    "source_schema": self.settings.schema,
                    "detector_fallback": detector_fallback,
                    "keypoints": keypoints,
                }
            )

        if not instances and not warnings:
            warnings.append("No pose instance was detected.")

        return {
            "status": "completed",
            "provider": "rtmpose",
            "model_name": self.settings.model,
            "device": self.settings.device,
            "width": width,
            "height": height,
            "inference_ms": round(inference_ms, 3),
            "instances": instances,
            "warnings": warnings,
        }