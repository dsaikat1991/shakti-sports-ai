import unittest

from app.services.athletics.models import (
    EventAnalysisRequest,
)
from app.services.athletics.router import (
    analyze_athletics_event,
)


class TestEventContracts(unittest.TestCase):
    def test_all_events_share_same_result_shape(self) -> None:
        required_keys = {
            "event",
            "status",
            "readiness",
            "phases",
            "metrics",
            "limitations",
            "analyzer_version",
        }

        for event in (
            "sprint",
            "hurdles",
            "long_jump",
            "high_jump",
        ):
            result = analyze_athletics_event(
                EventAnalysisRequest(
                    event=event,
                ),
                core_biomechanics={
                    "status": "completed",
                },
            )

            self.assertTrue(
                required_keys.issubset(
                    result.keys()
                )
            )


if __name__ == "__main__":
    unittest.main()
