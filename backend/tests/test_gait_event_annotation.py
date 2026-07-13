import tempfile
import unittest
from pathlib import Path

from app.services.biomechanics.gait_event_annotation import (
    load_gait_events,
    save_gait_events,
)
from app.services.biomechanics.gait_event_models import (
    GaitEvent,
)


class TestGaitEventAnnotation(unittest.TestCase):
    def test_round_trip(self) -> None:
        events = [
            GaitEvent(
                event_type="initial_contact",
                side="left",
                timestamp_ms=1000,
                frame_index=30,
                source="manual",
            )
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.json"

            save_gait_events(
                path,
                events,
                video_id="video-01",
            )

            loaded = load_gait_events(path)

        self.assertEqual(
            loaded,
            events,
        )


if __name__ == "__main__":
    unittest.main()
