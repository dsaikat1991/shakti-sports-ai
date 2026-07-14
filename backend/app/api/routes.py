from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.services.jobs.store import JobStatus, job_store
from app.services.pose.analyzer import analyze_video

router = APIRouter()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}

# Completed/failed jobs older than this are dropped on each new
# submission, so the in-memory store doesn't grow without bound.
JOB_RETENTION_MINUTES = 60


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "shakti-motion-intelligence",
    }


def _run_analysis_job(job_id: str, video_path: Path) -> None:
    """
    Background job body: runs the (potentially slow) pose analysis and
    records the outcome on the job, regardless of how it ends.

    Executed via FastAPI's BackgroundTasks, which runs synchronous
    callables in Starlette's threadpool - this keeps a multi-minute
    analysis from blocking the event loop, without needing an external
    task queue yet.
    """
    job_store.mark_processing(job_id)

    try:
        result = analyze_video(str(video_path))
        job_store.mark_completed(job_id, result)

    except Exception as error:  # noqa: BLE001 - job failure is reported, not raised
        job_store.mark_failed(job_id, str(error))

    finally:
        video_path.unlink(missing_ok=True)


@router.post("/analyze/video", status_code=202)
async def analyze_uploaded_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict:
    """
    Accept a video upload and analyze it in the background.

    Pose analysis can take anywhere from several seconds to several
    minutes depending on clip length and model - too long for a client
    to reliably wait on inside a single blocking request. This endpoint
    returns a job_id immediately; poll GET /analyze/video/{job_id} for
    status and, once complete, the result.
    """
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
    finally:
        await file.close()

    job = job_store.create()
    background_tasks.add_task(_run_analysis_job, job.id, temp_path)

    job_store.prune_finished_older_than(minutes=JOB_RETENTION_MINUTES)

    return {
        "job_id": job.id,
        "status": job.status.value,
    }


@router.get("/analyze/video/{job_id}")
async def get_analysis_job(job_id: str) -> dict:
    job = job_store.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis job found with id '{job_id}'.",
        )

    response = job.to_dict()

    if job.status == JobStatus.FAILED:
        response["error"] = job.error or "Pose analysis failed."

    return response
