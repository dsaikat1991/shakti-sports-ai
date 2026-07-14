import io
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


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


if __name__ == "__main__":
    unittest.main()
