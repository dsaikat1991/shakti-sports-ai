from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.biomechanics.gait_event_models import (
    GaitEvent,
)


def load_gait_events(
    file_path: str | Path,
) -> list[GaitEvent]:
    path = Path(file_path)

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    raw_events = payload.get("events", [])

    return [
        GaitEvent(
            event_type=item["event_type"],
            side=item["side"],
            timestamp_ms=int(item["timestamp_ms"]),
            frame_index=(
                int(item["frame_index"])
                if item.get("frame_index") is not None
                else None
            ),
            confidence=(
                float(item["confidence"])
                if item.get("confidence") is not None
                else None
            ),
            source=str(item.get("source", "manual")),
        )
        for item in raw_events
    ]


def save_gait_events(
    file_path: str | Path,
    events: list[GaitEvent],
    *,
    video_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    path = Path(file_path)

    payload = {
        "video_id": video_id,
        "metadata": metadata or {},
        "events": [
            event.to_dict()
            for event in events
        ],
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )
