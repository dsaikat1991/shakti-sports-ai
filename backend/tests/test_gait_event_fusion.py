import unittest

from app.services.biomechanics.gait_event_fusion import (
    EventCandidate,
    SignalVote,
    enforce_event_sequence,
    fuse_votes,
    resolve_candidate,
)


class TestGaitEventFusion(unittest.TestCase):
    def test_reliable_votes_fuse_high(self) -> None:
        votes = (
            SignalVote("a", 0.90, 0.95, 1.0, True),
            SignalVote("b", 0.85, 0.90, 1.0, True),
            SignalVote("c", 0.80, 0.90, 1.0, True),
        )

        result = fuse_votes(votes)

        self.assertEqual(result["status"], "fused")
        self.assertGreater(result["score"], 0.75)

    def test_low_reliability_reduces_acceptance(self) -> None:
        candidate = EventCandidate(
            event_type="initial_contact",
            side="left",
            timestamp_ms=1000,
            frame_index=30,
            votes=(
                SignalVote("a", 0.9, 0.2, 1.0, True),
                SignalVote("b", 0.9, 0.2, 1.0, True),
                SignalVote("c", 0.9, 0.2, 1.0, True),
            ),
        )

        result = resolve_candidate(
            candidate,
            threshold=0.80,
        )

        self.assertFalse(result["accepted"])

    def test_sequence_rejects_toe_off_before_contact(self) -> None:
        toe_off = EventCandidate(
            event_type="toe_off",
            side="left",
            timestamp_ms=1000,
            frame_index=30,
            votes=(
                SignalVote("a", 1.0, 1.0, 1.0, True),
                SignalVote("b", 1.0, 1.0, 1.0, True),
                SignalVote("c", 1.0, 1.0, 1.0, True),
            ),
        )

        resolved = resolve_candidate(
            toe_off,
            threshold=0.60,
        )

        result = enforce_event_sequence([resolved])

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )


if __name__ == "__main__":
    unittest.main()
