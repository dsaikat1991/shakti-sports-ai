from pathlib import Path
import shutil

from fastapi import APIRouter, File, UploadFile

from app.services.pose_service import analyze_video

router = APIRouter()


TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "shakti-motion-intelligence",
    }


@router.post("/analyze/video")
async def analyze_uploaded_video(
    file: UploadFile = File(...)
):
    temp_path = TEMP_DIR / file.filename

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    analysis = analyze_video(str(temp_path))

    temp_path.unlink(missing_ok=True)

    return analysis