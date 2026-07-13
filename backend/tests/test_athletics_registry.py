import unittest

from app.services.athletics.registry import (
    create_default_athletics_registry,
)


class TestAthleticsRegistry(unittest.TestCase):
    def test_only_supported_events_are_registered(self) -> None:
        registry = create_default_athletics_registry()

        self.assertEqual(
            registry.available_events(),
            (
                "high_jump",
                "hurdles",
                "long_jump",
                "sprint",
            ),
        )


if __name__ == "__main__":
    unittest.main()
