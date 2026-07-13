# Shakti RTMPose Live Integration v2.0

This package uses a separate RTMPose worker because your main Shakti backend and the OpenMMLab environment use different Python versions.

## 1. Copy the files

Copy the following into `D:\shaktisportsai\backend`:

- `rtmpose_worker/`
- `app/services/pose_remote/`
- `scripts/`
- `requirements-worker-extra.txt`
- `.env.rtmpose-live.example`

Do not overwrite your current MediaPipe or biomechanics services.

## 2. Activate RTMPose environment

```powershell
.\.venv-rtmpose\Scripts\Activate.ps1
```

## 3. Install worker-only dependencies

```powershell
python -m pip install -r requirements-worker-extra.txt -c rtmpose-constraints.txt
```

This does not reinstall Torch, MMCV, MMDetection or MMPose.

## 4. Set model variables

Start with RTMPose-t Halpe-26 at 256x192 for the GTX 1650:

```powershell
$env:RTMPOSE_MODEL="rtmpose-t_8xb1024-700e_body8-halpe26-256x192"
$env:RTMPOSE_DEVICE="cuda:0"
$env:RTMPOSE_SCHEMA="halpe26"
```

## 5. Start worker

```powershell
python -m uvicorn rtmpose_worker.app:app --host 127.0.0.1 --port 8011
```

Keep this PowerShell window open.

## 6. Smoke test from a second PowerShell window

```powershell
python scripts/smoke_test_worker.py path\to\sprint_frame.jpg
```

## 7. Benchmark

```powershell
python scripts/benchmark_rtmpose.py path\to\sprint_frame.jpg --runs 20
```

## 8. Call from the main backend

```python
from app.services.pose_remote.client import RTMPoseWorkerClient
from app.services.pose_remote.adapter import to_shakti_landmarks

client = RTMPoseWorkerClient()
result = client.infer_image_file("frame.jpg")
landmarks = to_shakti_landmarks(result)
```

## Safeguards

- Keep MediaPipe as fallback.
- Use batch size 1 initially.
- Avoid concurrent videos on the GTX 1650 until measured.
- Validate heel strike and toe-off against labelled frames.
- Model FPS is not complete video-pipeline FPS.
