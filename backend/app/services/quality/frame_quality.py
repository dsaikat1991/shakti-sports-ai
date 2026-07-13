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