import io
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


class _FakeStreamResponse:
    def __init__(self, status_code: int, chunks: list[bytes]) -> None:
        self.status_code = status_code
        self._chunks = chunks

    async def aiter_bytes(self):
        for chunk in self._chunks:
            yield chunk

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False


class _FakeAsyncClient:
    """Stands in for httpx.AsyncClient so tests never hit the network."""

    def __init__(self, response: _FakeStreamResponse) -> None:
        self._response = response

    def stream(self, method: str, url: str):
        return self._response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False


class TestAnalyzeVideoRoute(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _poll_until_finished(self, job_id: str, *, timeout_seconds: float = 5.0) -> dict:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = self.client.get(f"/api/analyze/video/{job_id}")
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            if payload["status"] in ("completed", "failed"):
                return payload
            time.sleep(0.05)
        self.fail(f"Job {job_id} did not finish within {timeout_seconds}s")

    def test_submit_then_poll_returns_completed_result(self) -> None:
        fake_result = {"video": {"total_frames": 10}, "biomechanics": {"status": "completed"}}

        with patch("app.api.routes.analyze_video", return_value=fake_result) as mock_analyze:
            response = self.client.post(
                "/api/analyze/video",
                files={"file": ("clip.mp4", io.BytesIO(b"not a real video"), "video/mp4")},
            )

            self.assertEqual(response.status_code, 202)
            submitted = response.json()
            self.assertEqual(submitted["status"], "queued")
            self.assertIn("job_id", submitted)

            final = self._poll_until_finished(submitted["job_id"])

        self.assertEqual(final["status"], "completed")
        self.assertEqual(final["result"], fake_result)
        self.assertIsNone(final["error"])
        mock_analyze.assert_called_once()

    def test_analysis_failure_is_reported_not_raised(self) -> None:
        with patch(
            "app.api.routes.analyze_video",
            side_effect=ValueError("Could not open uploaded video."),
        ):
            response = self.client.post(
                "/api/analyze/video",
                files={"file": ("clip.mp4", io.BytesIO(b"garbage"), "video/mp4")},
            )
            self.assertEqual(response.status_code, 202)
            job_id = response.json()["job_id"]

            final = self._poll_until_finished(job_id)

        self.assertEqual(final["status"], "failed")
        self.assertIn("Could not open uploaded video.", final["error"])

    def test_rejects_unsupported_content_type(self) -> None:
        response = self.client.post(
            "/api/analyze/video",
            files={"file": ("clip.txt", io.BytesIO(b"nope"), "text/plain")},
        )

        self.assertEqual(response.status_code, 415)

    def test_unknown_job_id_returns_404(self) -> None:
        response = self.client.get("/api/analyze/video/does-not-exist")
        self.assertEqual(response.status_code, 404)


class TestAnalyzeVideoUrlRoute(unittest.TestCase):
    """
    /analyze/video-url downloads the video server-side from a client-
    supplied URL - an SSRF vector if unconstrained. These tests exist
    mainly to lock in the host/path/scheme allowlist in
    _validate_signed_video_url, not just the happy path.
    """

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.valid_url = (
            "https://hdtrkuhjzvmywneodeiq.supabase.co/storage/v1/object/"
            "sign/performance-recordings/athlete-id/clip.mp4?token=abc"
        )

    def _poll_until_finished(
        self, job_id: str, *, timeout_seconds: float = 5.0
    ) -> dict:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = self.client.get(f"/api/analyze/video/{job_id}")
            payload = response.json()
            if payload["status"] in ("completed", "failed"):
                return payload
            time.sleep(0.05)
        self.fail(f"Job {job_id} did not finish within {timeout_seconds}s")

    def test_rejects_non_https_scheme(self) -> None:
        response = self.client.post(
            "/api/analyze/video-url",
            json={"video_url": self.valid_url.replace("https://", "http://")},
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_disallowed_host(self) -> None:
        response = self.client.post(
            "/api/analyze/video-url",
            json={
                "video_url": self.valid_url.replace(
                    "hdtrkuhjzvmywneodeiq.supabase.co", "evil.example.com"
                )
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_path_outside_signed_storage_prefix(self) -> None:
        response = self.client.post(
            "/api/analyze/video-url",
            json={
                "video_url": (
                    "https://hdtrkuhjzvmywneodeiq.supabase.co"
                    "/rest/v1/performances?select=*"
                )
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_path_on_allowed_host_but_wrong_bucket(self) -> None:
        response = self.client.post(
            "/api/analyze/video-url",
            json={
                "video_url": self.valid_url.replace(
                    "performance-recordings", "some-other-bucket"
                )
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_unsupported_suffix(self) -> None:
        response = self.client.post(
            "/api/analyze/video-url",
            json={"video_url": self.valid_url.replace(".mp4", ".exe")},
        )
        self.assertEqual(response.status_code, 415)

    def test_downloads_and_analyzes_successfully(self) -> None:
        fake_result = {
            "video": {"total_frames": 5},
            "biomechanics": {"status": "completed"},
        }
        fake_client = _FakeAsyncClient(
            _FakeStreamResponse(200, [b"chunk-one", b"chunk-two"])
        )

        with (
            patch("app.api.routes.analyze_video", return_value=fake_result),
            patch(
                "app.api.routes.httpx.AsyncClient", return_value=fake_client
            ),
        ):
            response = self.client.post(
                "/api/analyze/video-url", json={"video_url": self.valid_url}
            )
            self.assertEqual(response.status_code, 202)
            job_id = response.json()["job_id"]

            final = self._poll_until_finished(job_id)

        self.assertEqual(final["status"], "completed")
        self.assertEqual(final["result"], fake_result)

    def test_download_failure_returns_502(self) -> None:
        fake_client = _FakeAsyncClient(_FakeStreamResponse(403, []))

        with patch(
            "app.api.routes.httpx.AsyncClient", return_value=fake_client
        ):
            response = self.client.post(
                "/api/analyze/video-url", json={"video_url": self.valid_url}
            )

        self.assertEqual(response.status_code, 502)

    def test_oversized_download_returns_413(self) -> None:
        fake_client = _FakeAsyncClient(
            _FakeStreamResponse(200, [b"x" * 20])
        )

        with (
            patch(
                "app.api.routes.httpx.AsyncClient", return_value=fake_client
            ),
            patch.object(routes, "MAX_VIDEO_DOWNLOAD_BYTES", 10),
        ):
            response = self.client.post(
                "/api/analyze/video-url", json={"video_url": self.valid_url}
            )

        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
