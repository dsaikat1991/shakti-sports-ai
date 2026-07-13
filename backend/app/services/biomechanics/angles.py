from __future__ import annotations

from math import acos, degrees, sqrt
from typing import Any

from app.services.biomechanics.joint_names import (
    LEFT_ANKLE,
    LEFT_ELBOW,
    LEFT_HIP,
    LEFT_KNEE,
    LEFT_SHOULDER,
    LEFT_WRIST,
    RIGHT_ANKLE,
    RIGHT_ELBOW,
    RIGHT_HIP,
    RIGHT_KNEE,
    RIGHT_SHOULDER,
    RIGHT_WRIST,
)
from app.services.pose.landmark_usability import (
    landmark_is_usable,
    policy_for_backend,
)


MIN_LANDMARK_CONFIDENCE = 0.50


def _get_coordinate(
    point: Any,
    coordinate: str,
) -> float:
    """
    Read a coordinate from either:

    - a MediaPipe/legacy landmark object
    - a dictionary such as {"x": 0.5, "y": 0.4}
    - a tuple/list such as (0.5, 0.4)
    """

    if isinstance(point, dict):
        value = point.get(coordinate)

        if value is None:
            raise ValueError(
                f"Point is missing the '{coordinate}' coordinate."
            )

        return float(value)

    if isinstance(point, (tuple, list)):
        coordinate_index = {
            "x": 0,
            "y": 1,
            "z": 2,
        }[coordinate]

        if len(point) <= coordinate_index:
            raise ValueError(
                f"Point is missing the '{coordinate}' coordinate."
            )

        return float(point[coordinate_index])

    if hasattr(point, coordinate):
        return float(
            getattr(
                point,
                coordinate,
            )
        )

    raise ValueError(
        f"Point does not provide a '{coordinate}' coordinate."
    )


def landmark_is_reliable(
    landmark: Any,
    minimum_confidence: float | None = None,
    *,
    backend: str = "mediapipe",
) -> bool:
    """
    Return True when a landmark is reliable and lies within the normalized
    image frame.

    Confidence semantics are backend-aware:

    - MediaPipe defaults to visibility/presence >= 0.50
    - RTMPose defaults to confidence >= 0.35

    ``minimum_confidence`` remains available as an explicit override for
    backwards compatibility and tests.

    Plain tuples and dictionaries without confidence metadata are accepted
    after coordinate validation, preserving the original unit-test behavior.
    """

    try:
        x = _get_coordinate(
            landmark,
            "x",
        )
        y = _get_coordinate(
            landmark,
            "y",
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return False

    if (
        not 0.0 <= x <= 1.0
        or not 0.0 <= y <= 1.0
    ):
        return False

    if isinstance(
        landmark,
        (tuple, list),
    ):
        return True

    if isinstance(
        landmark,
        dict,
    ):
        has_quality_metadata = any(
            key in landmark
            for key in (
                "confidence",
                "visibility",
                "presence",
            )
        )
    else:
        has_quality_metadata = any(
            hasattr(
                landmark,
                name,
            )
            for name in (
                "confidence",
                "visibility",
                "presence",
            )
        )

    if not has_quality_metadata:
        return True

    if minimum_confidence is not None:
        return landmark_is_usable(
            landmark,
            backend=backend,
            minimum_confidence=minimum_confidence,
        )

    return landmark_is_usable(
        landmark,
        backend=backend,
        policy=policy_for_backend(
            backend
        ),
    )


def calculate_angle(
    point_a: Any,
    point_b: Any,
    point_c: Any,
    *,
    use_3d: bool = False,
) -> float:
    """
    Calculate angle A-B-C in degrees.

    Point B is the vertex. The result is between 0 and 180 degrees.

    By default, x/y image coordinates are used. Set ``use_3d=True`` only
    when calibrated and reliable 3D coordinates are available.
    """

    coordinates = (
        ("x", "y", "z")
        if use_3d
        else ("x", "y")
    )

    vector_ba = [
        _get_coordinate(
            point_a,
            coordinate,
        )
        - _get_coordinate(
            point_b,
            coordinate,
        )
        for coordinate in coordinates
    ]

    vector_bc = [
        _get_coordinate(
            point_c,
            coordinate,
        )
        - _get_coordinate(
            point_b,
            coordinate,
        )
        for coordinate in coordinates
    ]

    magnitude_ba = sqrt(
        sum(
            component**2
            for component in vector_ba
        )
    )

    magnitude_bc = sqrt(
        sum(
            component**2
            for component in vector_bc
        )
    )

    if (
        magnitude_ba == 0.0
        or magnitude_bc == 0.0
    ):
        raise ValueError(
            "Cannot calculate an angle from overlapping points."
        )

    dot_product = sum(
        first * second
        for first, second in zip(
            vector_ba,
            vector_bc,
            strict=True,
        )
    )

    cosine_value = (
        dot_product
        / (
            magnitude_ba
            * magnitude_bc
        )
    )

    cosine_value = max(
        -1.0,
        min(
            1.0,
            cosine_value,
        ),
    )

    return round(
        degrees(
            acos(
                cosine_value
            )
        ),
        2,
    )


def calculate_joint_angle(
    landmarks: list[Any],
    point_a_index: int,
    point_b_index: int,
    point_c_index: int,
    *,
    minimum_confidence: float | None = None,
    backend: str = "mediapipe",
) -> float | None:
    """
    Safely calculate a joint angle from a legacy landmark collection.

    Returns ``None`` when any required landmark is absent or unreliable.
    """

    required_indices = (
        point_a_index,
        point_b_index,
        point_c_index,
    )

    if any(
        index >= len(
            landmarks
        )
        for index in required_indices
    ):
        return None

    point_a = landmarks[
        point_a_index
    ]
    point_b = landmarks[
        point_b_index
    ]
    point_c = landmarks[
        point_c_index
    ]

    if not all(
        landmark_is_reliable(
            landmark,
            minimum_confidence,
            backend=backend,
        )
        for landmark in (
            point_a,
            point_b,
            point_c,
        )
    ):
        return None

    try:
        return calculate_angle(
            point_a,
            point_b,
            point_c,
        )
    except ValueError:
        return None


def calculate_knee_angles(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
    minimum_confidence: float | None = None,
) -> dict[str, float | None]:
    return {
        "left_knee": (
            calculate_joint_angle(
                landmarks,
                LEFT_HIP,
                LEFT_KNEE,
                LEFT_ANKLE,
                backend=backend,
                minimum_confidence=minimum_confidence,
            )
        ),
        "right_knee": (
            calculate_joint_angle(
                landmarks,
                RIGHT_HIP,
                RIGHT_KNEE,
                RIGHT_ANKLE,
                backend=backend,
                minimum_confidence=minimum_confidence,
            )
        ),
    }


def calculate_elbow_angles(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
    minimum_confidence: float | None = None,
) -> dict[str, float | None]:
    return {
        "left_elbow": (
            calculate_joint_angle(
                landmarks,
                LEFT_SHOULDER,
                LEFT_ELBOW,
                LEFT_WRIST,
                backend=backend,
                minimum_confidence=minimum_confidence,
            )
        ),
        "right_elbow": (
            calculate_joint_angle(
                landmarks,
                RIGHT_SHOULDER,
                RIGHT_ELBOW,
                RIGHT_WRIST,
                backend=backend,
                minimum_confidence=minimum_confidence,
            )
        ),
    }


def calculate_hip_angles(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
    minimum_confidence: float | None = None,
) -> dict[str, float | None]:
    """
    Estimate shoulder-hip-knee angle on each side.

    This remains a projected 2D angle and should not be interpreted as a
    laboratory-grade anatomical hip-extension measurement.
    """

    return {
        "left_hip": (
            calculate_joint_angle(
                landmarks,
                LEFT_SHOULDER,
                LEFT_HIP,
                LEFT_KNEE,
                backend=backend,
                minimum_confidence=minimum_confidence,
            )
        ),
        "right_hip": (
            calculate_joint_angle(
                landmarks,
                RIGHT_SHOULDER,
                RIGHT_HIP,
                RIGHT_KNEE,
                backend=backend,
                minimum_confidence=minimum_confidence,
            )
        ),
    }


def calculate_frame_joint_angles(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
    minimum_confidence: float | None = None,
) -> dict[str, float | None]:
    """
    Calculate the reusable joint-angle set for one frame.

    Existing callers remain compatible because MediaPipe stays the default.
    RTMPose callers should pass ``backend="rtmpose"``.
    """

    return {
        **calculate_knee_angles(
            landmarks,
            backend=backend,
            minimum_confidence=minimum_confidence,
        ),
        **calculate_elbow_angles(
            landmarks,
            backend=backend,
            minimum_confidence=minimum_confidence,
        ),
        **calculate_hip_angles(
            landmarks,
            backend=backend,
            minimum_confidence=minimum_confidence,
        ),
    }