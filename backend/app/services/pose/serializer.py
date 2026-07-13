from typing import Any


def serialize_landmarks(
    landmarks: list[Any],
) -> list[dict[str, float | int]]:
    return [
        {
            "index": index,
            "x": round(float(landmark.x), 6),
            "y": round(float(landmark.y), 6),
            "z": round(float(landmark.z), 6),
            "visibility": round(
                float(getattr(landmark, "visibility", 0.0)),
                6,
            ),
            "presence": round(
                float(getattr(landmark, "presence", 0.0)),
                6,
            ),
        }
        for index, landmark in enumerate(landmarks)
    ]