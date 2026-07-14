import unittest
from unittest.mock import patch

from app.services.pose_remote.live_analyzer import _connect_worker


class TestConnectWorker(unittest.TestCase):
    def test_unreachable_worker_raises_clear_runtime_error(self) -> None:
        with patch(
            "app.services.pose_remote.live_analyzer.RTMPoseWorkerClient"
        ) as mock_client_cls:
            mock_client_cls.return_value.health.side_effect = ConnectionError(
                "connection refused"
            )

            with self.assertRaises(RuntimeError) as ctx:
                _connect_worker()

        message = str(ctx.exception)
        self.assertIn("not reachable", message)
        self.assertIn("uvicorn rtmpose_worker.app:app", message)

    def test_initializes_worker_when_not_already_initialized(self) -> None:
        with patch(
            "app.services.pose_remote.live_analyzer.RTMPoseWorkerClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.health.return_value = {"initialized": False}

            _connect_worker()

            mock_client.initialize.assert_called_once()

    def test_skips_initialize_when_already_ready(self) -> None:
        with patch(
            "app.services.pose_remote.live_analyzer.RTMPoseWorkerClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.health.return_value = {"initialized": True}

            _connect_worker()

            mock_client.initialize.assert_not_called()


if __name__ == "__main__":
    unittest.main()
