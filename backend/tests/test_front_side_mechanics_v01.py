import unittest

from app.services.sprint.front_side_integration import (
    analyze_front_side_by_phase,
)
from app.services.sprint.front_side_mechanics import (
    analyze_front_side_mechanics,
)
from app.services.sprint.front_side_models import (
    FrontSideFrame,
)


def build_frame(
    index: int,
    *,
    side: str = "left",
    phase: str = "maximum_velocity",
    foot_x: float = 0.52,
) -> FrontSideFrame:
    return FrontSideFrame(
        frame_index=index,
        timestamp_ms=index * 40,
        phase=phase,
        side=side,
        hip_x=0.50,
        hip_y=0.50,
        knee_x=0.55,
        knee_y=0.35 - index * 0.005,
        ankle_x=0.58,
        ankle_y=0.68,
        foot_x=foot_x,
        foot_y=0.72,
        com_x=0.50,
        com_y=0.48,
        knee_angle_deg=85.0,
        hip_angle_deg=110.0,
        knee_angular_velocity_dps=650.0 + index * 20.0,
        confidence=0.95,
    )


class TestFrontSideMechanicsV01(
    unittest.TestCase
):
    def test_returns_front_side_metrics(self) -> None:
        frames = [
            build_frame(index)
            for index in range(5)
        ]

        result = analyze_front_side_mechanics(
            frames,
            side="left",
            phase="maximum_velocity",
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        metrics = result[
            "metrics"
        ]

        self.assertGreater(
            metrics[
                "maximum_knee_lift_body_height_percent"
            ],
            0.0,
        )

        self.assertGreater(
            metrics[
                "peak_knee_recovery_velocity_dps"
            ],
            0.0,
        )

        self.assertIsNotNone(
            metrics["score"]
        )

    def test_flags_large_foot_offset(self) -> None:
        frames = [
            build_frame(
                index,
                foot_x=0.72,
            )
            for index in range(5)
        ]

        result = analyze_front_side_mechanics(
            frames,
            side="left",
            phase="maximum_velocity",
        )

        self.assertEqual(
            result[
                "metrics"
            ]["overstride_risk"],
            "high",
        )

    def test_requires_minimum_frames(self) -> None:
        result = analyze_front_side_mechanics(
            [
                build_frame(0),
                build_frame(1),
            ],
            side="left",
            phase="maximum_velocity",
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )

    def test_phase_integration(self) -> None:
        frames = []

        for side in (
            "left",
            "right",
        ):
            for phase in (
                "drive",
                "transition",
                "maximum_velocity",
            ):
                frames.extend(
                    [
                        build_frame(
                            index,
                            side=side,
                            phase=phase,
                        )
                        for index in range(4)
                    ]
                )

        result = analyze_front_side_by_phase(
            frames
        )

        self.assertIn(
            "left",
            result["sides"],
        )

        self.assertIn(
            "maximum_velocity",
            result[
                "sides"
            ]["right"],
        )


if __name__ == "__main__":
    unittest.main()
