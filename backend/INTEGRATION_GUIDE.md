# Backend-aware landmark usability integration

## Goal

Keep MediaPipe at a 0.50 visibility/presence threshold while allowing
RTMPose landmarks to use a separately calibrated 0.35 confidence threshold.

## Copy these files

```text
app/services/pose/landmark_usability.py
app/services/pose/pose_quality_policy.py
tests/test_landmark_usability_v10.py
```

## Replace direct landmark checks

Where an extractor currently calls:

```python
landmark_is_usable(landmark)
```

change it to:

```python
from app.services.pose.landmark_usability import landmark_is_usable

landmark_is_usable(
    landmark,
    backend=frame.backend,
)
```

For legacy extractor APIs that do not receive a frame object, pass the backend
explicitly from the segment orchestration layer.

## Provenance

```python
from app.services.pose.pose_quality_policy import (
    build_pose_quality_policy_report,
)

result["pose_quality_policy"] = build_pose_quality_policy_report(backend)
```

## Rerun

```powershell
python -m unittest discover -s tests -v
```

Then rerun the segment-biomechanics command on the same clip and compare:

- usable landmark coverage,
- consecutive usable-frame runs,
- cadence status,
- contact-event count,
- joint-angle coverage.

Do not lower RTMPose below 0.35 until manually labelled validation supports it.
