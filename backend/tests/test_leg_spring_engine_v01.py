import unittest

from app.services.sprint.leg_spring_engine import (
    analyze_leg_spring,
    analyze_leg_spring_by_phase,
)
from app.services.sprint.leg_spring_models import (
    LegSpringFrame,
)
from app.services.sprint.leg_spring_report import (
    build_leg_spring_report,
)
from app.services.sprint.leg_spring_symmetry import (
    build_leg_spring_symmetry,
)


def make_frame(
    index: int,
    *,
    side: str = "left",
    phase: str = "maximum_velocity",
    com_y: float | None = None,
) -> LegSpringFrame:
    compression_pattern = [
        0.50,
        0.53,
        0.56,
        0.58,
        0.56,
        0.53,
        0.51,
    ]

    if com_y is None:
        com_y = compression_pattern[
            min(
                index,
                len(compression_pattern) - 1,
            )
        ]

    return LegSpringFrame(
        frame_index=index,
        timestamp_ms=index * 20,
        side=side,
        phase=phase,
        com_y=com_y,
        hip_y=0.48,
        knee_y=0.66,
        ankle_y=0.82,
        foot_y=0.86,
        contact_probability=0.92,
        toe_off_probability=(
            0.90
            if index == 6
            else 0.10
        ),
        ground_contact_ms=120.0,
        flight_time_ms=105.0,
        cadence_spm=286.0,
        confidence=0.94,
    )


class TestLegSpringEngineV01(
    unittest.TestCase
):
    def test_returns_leg_spring_metrics(
        self,
    ) -> None:
        result = analyze_leg_spring(
            [
                make_frame(index)
                for index in range(7)
            ],
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
                "estimated_leg_compression_normalized"
            ],
            0.0,
        )

        self.assertIsNotNone(
            metrics[
                "elastic_return_ratio"
            ]
        )

        self.assertIsNotNone(
            metrics[
                "overall_leg_spring_score"
            ]
        )

    def test_poor_return_reduces_score(
        self,
    ) -> None:
        good = analyze_leg_spring(
            [
                make_frame(index)
                for index in range(7)
            ],
            side="left",
            phase="maximum_velocity",
        )

        bad_pattern = [
            0.50,
            0.53,
            0.56,
            0.59,
            0.60,
            0.60,
            0.60,
        ]

        bad = analyze_leg_spring(
            [
                make_frame(
                    index,
                    com_y=bad_pattern[index],
                )
                for index in range(7)
            ],
            side="left",
            phase="maximum_velocity",
        )

        self.assertGreater(
            good["metrics"][
                "overall_leg_spring_score"
            ],
            bad["metrics"][
                "overall_leg_spring_score"
            ],
        )

    def test_left_right_symmetry(
        self,
    ) -> None:
        left = analyze_leg_spring(
            [
                make_frame(
                    index,
                    side="left",
                )
                for index in range(7)
            ],
            side="left",
            phase="maximum_velocity",
        )

        right = analyze_leg_spring(
            [
                make_frame(
                    index,
                    side="right",
                )
                for index in range(7)
            ],
            side="right",
            phase="maximum_velocity",
        )

        symmetry = build_leg_spring_symmetry(
            left,
            right,
        )

        self.assertEqual(
            symmetry["status"],
            "completed",
        )

        self.assertGreater(
            symmetry["symmetry_score"],
            95.0,
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
                        )
                        for index in range(7)
                    ]
                )

        result = (
            analyze_leg_spring_by_phase(
                frames
            )
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

        self.assertIsNotNone(
            result[
                "overall_average_leg_spring_score"
            ]
        )

    def test_report_and_insufficient_data(
        self,
    ) -> None:
        insufficient = analyze_leg_spring(
            [
                make_frame(index)
                for index in range(3)
            ],
            side="left",
            phase="drive",
        )

        self.assertEqual(
            insufficient["status"],
            "insufficient_data",
        )

        full = analyze_leg_spring(
            [
                make_frame(index)
                for index in range(7)
            ],
            side="left",
            phase="maximum_velocity",
        )

        report = build_leg_spring_report(
            full
        )

        self.assertEqual(
            report["status"],
            "completed",
        )


if __name__ == "__main__":
    unittest.main()
