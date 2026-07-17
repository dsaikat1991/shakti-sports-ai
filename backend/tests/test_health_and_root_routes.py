import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestHealthAndRootRoutes(unittest.TestCase):
    """
    GET / and GET /api/health previously had no test coverage at all
    (flagged in the full-repo red-flag audit) - trivial handlers, but a
    genuine gap. Added as part of the Milestone C low-risk cleanup pass.
    """

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_root_returns_service_info(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], "Shakti Motion Intelligence API")
        self.assertEqual(body["status"], "running")

    def test_api_health_returns_healthy(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "healthy")
        self.assertEqual(body["service"], "shakti-motion-intelligence")


if __name__ == "__main__":
    unittest.main()
