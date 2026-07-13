from __future__ import annotations

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile

from rtmpose_worker.core import RTMPoseRuntime, Settings

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
    try:
        runtime.initialize()
        return {
            "status": "initialized",
            "model_name": settings.model,
            "device": settings.device,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/infer/image")
async def infer_image(file: UploadFile = File(...)) -> dict:
    try:
        image = runtime.decode_image(await file.read())
        return runtime.infer(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
