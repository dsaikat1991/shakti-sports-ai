from __future__ import annotations

import logging
import os

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile

from rtmpose_worker.core import RTMPoseRuntime, Settings

# Structured logging - previously absent from this service entirely
# (flagged in the full-repo red-flag audit): every error handler here
# converted an exception straight into an HTTPException with no
# server-side trace, so a crash on this GPU-backed process left nothing
# to debug beyond whatever uvicorn happened to print to stdout. Level is
# configurable via RTMPOSE_WORKER_LOG_LEVEL (default INFO) rather than
# hardcoded, so a deployment can turn on DEBUG without a code change.
logging.basicConfig(
    level=os.getenv("RTMPOSE_WORKER_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("rtmpose_worker")

settings = Settings.from_environment()
runtime = RTMPoseRuntime(settings)
app = FastAPI(title="Shakti RTMPose Worker", version="2.0.0")


@app.get("/health")
def health() -> dict:
    try:
        import mmpose
        mmpose_version = mmpose.__version__
    except Exception:
        mmpose_version = None

    cuda_available = torch.cuda.is_available()
    return {
        "status": "ready" if runtime.initialized else "not_initialized",
        "provider": "rtmpose",
        "model_name": settings.model,
        "device": settings.device,
        "torch_version": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cuda_available": cuda_available,
        "gpu_name": torch.cuda.get_device_name(0) if cuda_available else None,
        "mmpose_version": mmpose_version,
        "initialized": runtime.initialized,
        "initialization_error": runtime.initialization_error,
    }


@app.post("/initialize")
def initialize() -> dict:
    logger.info(
        "initialize requested (model=%s, device=%s)",
        settings.model,
        settings.device,
    )
    try:
        runtime.initialize()
        logger.info("initialize succeeded")
        return {
            "status": "initialized",
            "model_name": settings.model,
            "device": settings.device,
        }
    except Exception as exc:
        logger.exception("initialize failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/infer/image")
async def infer_image(file: UploadFile = File(...)) -> dict:
    try:
        image = runtime.decode_image(await file.read())
        return runtime.infer(image)
    except ValueError as exc:
        # Expected, client-caused failures (bad/corrupt image bytes) -
        # logged at warning level with no traceback noise, since these
        # are routine and not a worker-health signal.
        logger.warning("infer/image rejected input: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Unexpected failures (GPU OOM, model error, etc.) - logged with
        # a full traceback server-side before the client ever sees the
        # 500, so a worker crash is actually debuggable.
        logger.exception("infer/image failed unexpectedly")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
