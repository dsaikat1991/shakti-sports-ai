import unittest
from unittest.mock import patch

from app.main import _cors_allowed_origins


class TestCorsAllowedOrigins(unittest.TestCase):
    """
    Milestone C low-risk cleanup: CORS origins were previously hardcoded
    to the local Vite dev port only. Now environment-driven via
    CORS_ALLOWED_ORIGINS, with a hard guard against ever configuring a
    wildcard origin alongside allow_credentials=True.
    """

    def test_defaults_to_local_dev_origin_when_unset(self) -> None:
        with patch.dict("os.environ", {}, clear=False):
            import os as _os

            _os.environ.pop("CORS_ALLOWED_ORIGINS", None)
            self.assertEqual(_cors_allowed_origins(), ["http://localhost:5173"])

    def test_reads_comma_separated_origins_from_environment(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "CORS_ALLOWED_ORIGINS": "https://app.example.com,https://staging.example.com"
            },
        ):
            self.assertEqual(
                _cors_allowed_origins(),
                ["https://app.example.com", "https://staging.example.com"],
            )

    def test_trims_whitespace_and_drops_empty_entries(self) -> None:
        with patch.dict(
            "os.environ",
            {"CORS_ALLOWED_ORIGINS": " https://app.example.com , , https://b.example.com "},
        ):
            self.assertEqual(
                _cors_allowed_origins(),
                ["https://app.example.com", "https://b.example.com"],
            )

    def test_rejects_wildcard_origin(self) -> None:
        with patch.dict("os.environ", {"CORS_ALLOWED_ORIGINS": "*"}):
            with self.assertRaises(RuntimeError):
                _cors_allowed_origins()

    def test_rejects_wildcard_mixed_with_real_origins(self) -> None:
        with patch.dict(
            "os.environ", {"CORS_ALLOWED_ORIGINS": "https://app.example.com,*"}
        ):
            with self.assertRaises(RuntimeError):
                _cors_allowed_origins()


if __name__ == "__main__":
    unittest.main()
