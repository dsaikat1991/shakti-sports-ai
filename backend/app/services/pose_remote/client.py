from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx


class RTMPoseWorkerClient:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8011",
        timeout_seconds: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def health(self) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/health", timeout=self.timeout_seconds
        )
        if response.is_error:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text

            detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
            raise RuntimeError(
                f"RTMPose worker returned {response.status_code} "
                f"{response.reason_phrase}: {detail}"
            )

        return response.json()

    def initialize(self) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/initialize", timeout=self.timeout_seconds
        )
        if response.is_error:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text

            detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
            raise RuntimeError(
                f"RTMPose worker returned {response.status_code} "
                f"{response.reason_phrase}: {detail}"
            )

        return response.json()

    def infer_image_bytes(
        self,
        *,
        content: bytes,
        filename: str = "frame.jpg",
    ) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/infer/image",
            files={"file": (filename, content, "image/jpeg")},
            timeout=self.timeout_seconds,
        )
        if response.is_error:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text

            detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
            raise RuntimeError(
                f"RTMPose worker returned {response.status_code} "
                f"{response.reason_phrase}: {detail}"
            )

        return response.json()

    def infer_image_file(self, path: str | Path) -> dict[str, Any]:
        image_path = Path(path)
        return self.infer_image_bytes(
            content=image_path.read_bytes(), filename=image_path.name
        )