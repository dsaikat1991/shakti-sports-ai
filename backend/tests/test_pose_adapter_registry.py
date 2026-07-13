import unittest

from app.services.pose_adapters.registry import (
    create_default_registry,
)


class TestPoseAdapterRegistry(unittest.TestCase):
    def test_default_backends_are_registered(self) -> None:
        registry = create_default_registry()

        self.assertIn(
            "mediapipe",
            registry.available_backends(),
        )

        self.assertIn(
            "rtmpose",
            registry.available_backends(),
        )


if __name__ == "__main__":
    unittest.main()
