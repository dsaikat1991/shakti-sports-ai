from pathlib import Path
from urllib.parse import urlparse
import os
import shutil
import uuid

import httpx
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.jobs.store import JobStatus, job_store
from app.services.pose.analyzer import analyze_video as analyze_video_mediapipe
from app.services.pose_remote.live_analyzer import analyze_video as analyze_video_rtmpose

# RTMPose is the live pipeline: multi-person tracking/selection, gap
# interpolation, and the backend-aware confidence policy make it more
# robust to real-world footage than the MediaPipe path, which just
# takes the first detected pose per frame with no tracking. It does
# require rtmpose_worker to be running separately (GPU-backed) -
# analyze_video_rtmpose raises a clear, actionable error if it isn't,
# which _run_analysis_job below turns into a failed job rather than a
# server crash. analyze_video_mediapipe is kept available, in-process
# and with no external dependency, as a fallback path if needed.
analyze_video = analyze_video_rtmpose

router = APIRouter()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}

ALLOWED_VIDEO_SUFFIXES = {".mp4", ".mov", ".webm"}

# Completed/failed jobs older than this are dropped on each new
# submission, so the in-memory store doesn't grow without bound.
JOB_RETENTION_MINUTES = 60

# --- /analyze/video-url: server-side download from a Supabase Storage
# signed URL, instead of the client re-uploading the video a second time.
# See docs/ANALYSIS_WORKFLOW_AUDIT.md section 4 for the full design and
# threat model. video_url is client-supplied and fetched server-side,
# which is an SSRF vector if unconstrained - SUPABASE_STORAGE_HOST and
# SUPABASE_STORAGE_SIGNED_PATH_PREFIX below are an exact allowlist
# enforced by _validate_signed_video_url before any network call happens.
SUPABASE_STORAGE_HOST = os.getenv(
    "SUPABASE_STORAGE_HOST", "hdtrkuhjzvmywneodeiq.supabase.co"
)
SUPABASE_STORAGE_SIGNED_PATH_PREFIX = (
    "/storage/v1/object/sign/performance-recordings/"
)
MAX_VIDEO_DOWNLOAD_BYTES = 500 * 1024 * 1024
VIDEO_DOWNLOAD_TIMEOUT_SECONDS = 180.0


class AnalyzeVideoUrlRequest(BaseModel):
    video_url: str


def _validate_signed_video_url(video_url: str) -> str:
    """
    Returns the file suffix (e.g. ".mp4") on success; raises HTTPException
    on any validation failure. Deliberately strict and allowlist-based
    (exact host, exact path prefix, https-only) rather than a denylist -
    this is the only thing standing between this endpoint and SSRF.
    """
    parsed = urlparse(video_url)

    if parsed.scheme != "https":
        raise HTTPException(
            status_code=400, detail="video_url must use https."
        )

    if parsed.netloc != SUPABASE_STORAGE_HOST:
        raise HTTPException(
            status_code=400,
            detail="video_url host is not an allowed storage host.",
        )

    if not parsed.path.startswith(SUPABASE_STORAGE_SIGNED_PATH_PREFIX):
        raise HTTPException(
            status_code=400,
            detail=(
                "video_url must be a signed URL for the "
                "performance-recordings bucket."
            ),
        )

    suffix = Path(parsed.path).suffix.lower()
    if suffix not in ALLOWED_VIDEO_SUFFIXES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported video type. Upload an MP4, MOV, or WEBM file.",
        )

    return suffix


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


@router.post("/analyze/video-url", status_code=202)
async def analyze_video_from_url(
    background_tasks: BackgroundTasks,
    payload: AnalyzeVideoUrlRequest,
) -> dict:
    """
    Same job pipeline as POST /analyze/video, but the server downloads the
    video itself from a short-lived Supabase Storage signed URL instead of
    receiving the bytes directly from the client.

    Exists so the frontend can (re)submit analysis for an already-uploaded
    performance - e.g. a retry from the performance history page - without
    needing the original browser File object in memory, and without
    re-uploading the same video twice from the client on first submission.

    video_url must pass _validate_signed_video_url's host/path/scheme
    allowlist before any network request is made (SSRF guard - see that
    function's docstring and docs/ANALYSIS_WORKFLOW_AUDIT.md section 4).
    An expired or tampered signed token is still rejected - by Supabase,
    on the actual download - and surfaces as a normal failed job.
    """
    suffix = _validate_signed_video_url(payload.video_url)

    temp_path = TEMP_DIR / f"{uuid.uuid4()}{suffix}"
    downloaded_bytes = 0

    try:
        async with httpx.AsyncClient(
            timeout=VIDEO_DOWNLOAD_TIMEOUT_SECONDS
        ) as client:
            async with client.stream(
                "GET", payload.video_url
            ) as response:
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=(
                            f"Could not download video (status "
                            f"{response.status_code}). The link may "
                            "have expired - try again."
                        ),
                    )

                with temp_path.open("wb") as buffer:
                    async for chunk in response.aiter_bytes():
                        downloaded_bytes += len(chunk)

                        if downloaded_bytes > MAX_VIDEO_DOWNLOAD_BYTES:
                            raise HTTPException(
                                status_code=413,
                                detail="Video file is too large.",
                            )

                        buffer.write(chunk)

    except HTTPException:
        temp_path.unlink(missing_ok=True)
        raise

    except httpx.HTTPError as error:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=502,
            detail=f"Could not download video: {error}",
        ) from error

    job = job_store.create()
    background_tasks.add_task(_run_analysis_job, job.id, temp_path)

    job_store.prune_finished_older_than(minutes=JOB_RETENTION_MINUTES)

    return {
        "job_id": job.id,
        "status": job.status.value,
    }
