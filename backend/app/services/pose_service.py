import cv2


def analyze_video(video_path: str):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Could not open uploaded video.")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    duration = 0

    if fps > 0:
        duration = frame_count / fps

    cap.release()

    return {
        "frame_count": frame_count,
        "fps": round(fps, 2),
        "duration_seconds": round(duration, 2),
    }