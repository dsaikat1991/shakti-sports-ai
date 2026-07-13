import unittest

from app.services.sprint.propulsion_annotation import (
    build_contact_phase_annotations,
)
from app.services.sprint.propulsion_engine import (
    analyze_propulsion_braking,
    analyze_propulsion_braking_by_phase,
)
from app.services.sprint.propulsion_models import (
    ContactMotionFrame,
)
from app.services.sprint.propulsion_report import (
    build_propulsion_report,
)


def make_frame(
    index: int,
    *,
    side: str = "left",
    phase: str = "maximum_velocity",
    acceleration: float = 1.0,
    foot_x: float = 0.51,
) -> ContactMotionFrame:
    return ContactMotionFrame(
        frame_index=index,
        timestamp_ms=index * 40,
        side=side,
        phase=phase,
        com_velocity_x=8.0 + index * 0.05,
        com_acceleration_x=acceleration,
        foot_x=foot_x,
        com_x=0.50,
        shin_angle_deg=76.0,
        contact_probability=0.92,
        toe_off_probability=(
            0.90
            if index == 5
            else 0.25
        ),
        confidence=0.94,
    )


class TestPropulsionBrakingEngineV01(
    unittest.TestCase
):
    def test_propulsive_contact_scores_high(
        self,
    ) -> None:
        frames = [
            make_frame(
                index,
                acceleration=(
                    -0.5
                    if index < 2
                    else 1.6
                ),
            )
            for index in range(7)
        ]

        result = analyze_propulsion_braking(
            frames,
            side="left",
            phase="maximum_velocity",
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        metrics = result["metrics"]

        self.assertGreater(
            metrics[
                "propulsion_effectiveness_score"
            ],
            metrics["braking_index"],
        )

        self.assertGreater(
            metrics[
                "net_horizontal_propulsion_score"
            ],
            60.0,
        )

    def test_braking_heavy_contact_scores_lower(
        self,
    ) -> None:
        propulsive = analyze_propulsion_braking(
            [
                make_frame(
                    index,
                    acceleration=(
                        -0.2
                        if index == 0
                        else 1.5
                    ),
                )
                for index in range(7)
            ],
            side="left",
            phase="maximum_velocity",
        )

        braking = analyze_propulsion_braking(
            [
                make_frame(
                    index,
                    acceleration=(
                        -1.8
                        if index < 5
                        else 0.3
                    ),
                    foot_x=0.75,
                )
                for index in range(7)
            ],
            side="left",
            phase="maximum_velocity",
        )

        self.assertGreater(
            propulsive["metrics"][
                "net_horizontal_propulsion_score"
            ],
            braking["metrics"][
                "net_horizontal_propulsion_score"
            ],
        )

    def test_annotations_label_contact_direction(
        self,
    ) -> None:
        frames = [
            make_frame(
                0,
                acceleration=-1.0,
            ),
            make_frame(
                1,
                acceleration=1.0,
            ),
        ]

        annotations = (
            build_contact_phase_annotations(
                frames
            )
        )

        labels = {
            item["label"]
            for item in annotations
        }

        self.assertIn(
            "braking",
            labels,
        )

        self.assertIn(
            "propulsion",
            labels,
        )

    def test_by_phase_integration(
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
                        make_frame(
                            index,
                            side=side,
                            phase=phase,
                            acceleration=(
                                -0.4
                                if index < 2
                                else 1.3
                            ),
                        )
                        for index in range(6)
                    ]
                )

        result = (
            analyze_propulsion_braking_by_phase(
                frames
            )
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertIsNotNone(
            result[
                "overall_average_net_propulsion_score"
            ]
        )

    def test_report_and_insufficient_data(
        self,
    ) -> None:
        insufficient = (
            analyze_propulsion_braking(
                [
                    make_frame(0),
                    make_frame(1),
                ],
                side="left",
                phase="drive",
            )
        )

        self.assertEqual(
            insufficient["status"],
            "insufficient_data",
        )

        full = analyze_propulsion_braking(
            [
                make_frame(
                    index,
                    acceleration=(
                        -0.5
                        if index < 2
                        else 1.2
                    ),
                )
                for index in range(6)
            ],
            side="left",
            phase="maximum_velocity",
        )

        report = build_propulsion_report(
            full
        )

        self.assertEqual(
            report["status"],
            "completed",
        )


if __name__ == "__main__":
    unittest.main()
