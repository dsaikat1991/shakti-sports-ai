from pathlib import Path

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


BACKEND_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BACKEND_DIR / "models" / "pose_landmarker_full.task"


def create_pose_landmarker() -> vision.PoseLandmarker:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Pose Landmarker model was not found at: {MODEL_PATH}"
        )

    base_options = python.BaseOptions(
        model_asset_path=str(MODEL_PATH),
    )

    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )

    return vision.PoseLandmarker.create_from_options(options)