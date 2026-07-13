import unittest

from app.services.sprint.back_side_integration import (
    analyze_back_side_by_phase,
)
from app.services.sprint.back_side_mechanics import (
    analyze_back_side_mechanics,
)
from app.services.sprint.back_side_models import (
    BackSideFrame,
)
from app.services.sprint.metric_provenance import (
    build_metric_provenance,
)


def build_frame(
    index: int,
    *,
    side: str = "left",
    phase: str = "maximum_velocity",
    toe_x: float = 0.40,
    heel_velocity_x: float = 1.6,
) -> BackSideFrame:
    return BackSideFrame(
        frame_index=index,
        timestamp_ms=index * 40,
        phase=phase,
        side=side,
        shoulder_x=0.50,
        shoulder_y=0.25,
        hip_x=0.50,
        hip_y=0.50,
        knee_x=0.44,
        knee_y=0.66,
        ankle_x=0.41,
        ankle_y=0.82,
        heel_x=0.40,
        heel_y=0.84,
        toe_x=toe_x,
        toe_y=0.86,
        com_x=0.52,
        com_y=0.48,
        hip_angle_deg=145.0 + index,
        knee_angle_deg=150.0 + index,
        heel_velocity_x=(
            heel_velocity_x
            + index * 0.05
        ),
        heel_velocity_y=-0.4,
        ankle_velocity_x=1.2,
        ankle_velocity_y=-0.2,
        toe_off_probability=(
            0.90
            if index == 3
            else 0.40
        ),
        confidence=0.95,
    )


class TestBackSideMechanicsV01(
    unittest.TestCase
):
    def test_returns_back_side_metrics(
        self,
    ) -> None:
        frames = [
            build_frame(index)
            for index in range(5)
        ]

        result = (
            analyze_back_side_mechanics(
                frames,
                side="left",
                phase="maximum_velocity",
            )
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
                "maximum_hip_extension_deg"
            ],
            0.0,
        )

        self.assertGreater(
            metrics[
                "peak_heel_recovery_speed_normalized"
            ],
            0.0,
        )

        self.assertIsNotNone(
            metrics[
                "push_off_completion_score"
            ]
        )

        self.assertIsNotNone(
            metrics["score"]
        )

    def test_flags_excessive_back_side(
        self,
    ) -> None:
        frames = [
            build_frame(
                index,
                toe_x=0.20,
            )
            for index in range(8)
        ]

        result = (
            analyze_back_side_mechanics(
                frames,
                side="left",
                phase="maximum_velocity",
            )
        )

        self.assertEqual(
            result[
                "metrics"
            ]["back_side_risk"],
            "high",
        )

    def test_requires_minimum_frames(
        self,
    ) -> None:
        result = (
            analyze_back_side_mechanics(
                [
                    build_frame(0),
                    build_frame(1),
                ],
                side="left",
                phase="drive",
            )
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )

    def test_phase_integration(
        self,
    ) -> None:
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

        result = (
            analyze_back_side_by_phase(
                frames
            )
        )

        self.assertIn(
            "left",
            result["sides"],
        )

        self.assertIn(
            "transition",
            result[
                "sides"
            ]["right"],
        )

    def test_metric_provenance(
        self,
    ) -> None:
        provenance = (
            build_metric_provenance(
                metric_name=(
                    "maximum_hip_extension_deg"
                ),
                value=151.2,
                confidence=0.91,
                inputs=[
                    "left_shoulder",
                    "left_hip",
                    "left_knee",
                ],
                algorithm=(
                    "back_side_mechanics_v0.1"
                ),
                validation_status=(
                    "experimental"
                ),
                unit="deg",
            )
        )

        self.assertEqual(
            provenance["metric"],
            "maximum_hip_extension_deg",
        )

        self.assertEqual(
            provenance[
                "validation_status"
            ],
            "experimental",
        )


if __name__ == "__main__":
    unittest.main()
