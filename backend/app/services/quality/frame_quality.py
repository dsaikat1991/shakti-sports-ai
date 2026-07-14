import cv2
import numpy as np


def calculate_brightness(frame: np.ndarray) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def calculate_sharpness(frame: np.ndarray) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def score_brightness(brightness: float) -> float:
    if brightness < 30:
        return 10.0

    if brightness < 60:
        return 50.0

    if brightness <= 200:
        return 100.0

    if brightness <= 225:
        return 65.0

    return 25.0


def score_sharpness(sharpness: float) -> float:
    if sharpness < 20:
        return 15.0

    if sharpness < 50:
        return 45.0

    if sharpness < 100:
        return 75.0

    return 100.0


def score_fps(fps: float) -> float:
    if fps >= 50:
        return 100.0

    if fps >= 29:
        return 85.0

    if fps >= 24:
        return 70.0

    if fps >= 20:
        return 45.0

    return 20.0


def score_camera_height(headroom_percent: float) -> float:
    """
    Score how much empty space sits above the athlete's head.

    classify_camera_view catches wrong camera *rotation* (front/three-
    quarter vs side), but has no signal for camera *height/tilt* - a
    camera positioned low and tilted upward can still measure as a
    perfect side view by that check alone. Confirmed empirically: two
    known-bad clips (low, upward-tilted cameras that caused wrong
    ground-contact detection - see contact_events.py) both had roughly
    2x the headroom of a known-good, properly-framed clip. A low,
    upward-tilted camera leaves excess empty sky/background above the
    subject because the shot isn't level; a camera at roughly the
    athlete's own height frames them closer to vertically centred.

    This is one signal among several, not a hard gate on its own -
    thresholds are set from only 3 reference clips, so this should be
    revisited as more real footage is checked.
    """
    if headroom_percent < 0.25:
        return 100.0

    if headroom_percent < 0.32:
        return 60.0

    if headroom_percent < 0.40:
        return 30.0

    return 10.0