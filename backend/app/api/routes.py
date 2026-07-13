from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.pose.analyzer import analyze_video

router = APIRouter()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "shakti-motion-intelligence",
    }


@router.post("/analyze/video")
async def analyze_uploaded_video(
    file: UploadFile = File(...),
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported video type. "
                "Upload an MP4, MOV, or WEBM file."
            ),
        )

    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    temp_path = TEMP_DIR / f"{uuid.uuid4()}{suffix}"

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return analyze_video(str(temp_path))

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Pose analysis failed: {error}",
        ) from error

    finally:
        await file.close()
        temp_path.unlink(missing_ok=True)