import unittest

from app.services.sprint.stride_geometry_engine import (
    analyze_stride_geometry,
)
from app.services.sprint.stride_geometry_models import (
    FootContactEvent,
    StrideGeometryContext,
)
from app.services.sprint.stride_geometry_report import (
    build_stride_geometry_report,
)


def contact(
    index: int,
    *,
    side: str,
    foot_x: float,
    foot_y: float,
    com_x: float | None = None,
    com_y: float = 0.50,
) -> FootContactEvent:
    if com_x is None:
        com_x = foot_x - 0.02

    return FootContactEvent(
        side=side,
        frame_index=index,
        timestamp_ms=index * 120,
        foot_x=foot_x,
        foot_y=foot_y,
        com_x=com_x,
        com_y=com_y,
        toe_x=foot_x + 0.03,
        toe_y=foot_y,
        heel_x=foot_x - 0.03,
        heel_y=foot_y,
        confidence=0.94,
    )


class TestStrideGeometryEngineV01(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.context = StrideGeometryContext(
            body_height_normalized=0.70,
            leg_length_normalized=0.42,
            real_world_scale_m_per_unit=2.2,
            athlete_height_m=1.78,
        )

    def test_balanced_stride_geometry(
        self,
    ) -> None:
        contacts = [
            contact(
                0,
                side="left",
                foot_x=0.10,
                foot_y=0.44,
            ),
            contact(
                1,
                side="right",
                foot_x=0.58,
                foot_y=0.56,
            ),
            contact(
                2,
                side="left",
                foot_x=1.06,
                foot_y=0.44,
            ),
            contact(
                3,
                side="right",
                foot_x=1.54,
                foot_y=0.56,
            ),
            contact(
                4,
                side="left",
                foot_x=2.02,
                foot_y=0.44,
            ),
            contact(
                5,
                side="right",
                foot_x=2.50,
                foot_y=0.56,
            ),
        ]

        result = analyze_stride_geometry(
            contacts,
            context=self.context,
            cadence_spm=280.0,
            horizontal_velocity=2.2,
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        metrics = result["metrics"]

        self.assertGreater(
            metrics[
                "step_length_symmetry_score"
            ],
            90.0,
        )

        self.assertIsNotNone(
            metrics[
                "average_step_length_m"
            ]
        )

        self.assertIsNotNone(
            metrics[
                "overall_stride_geometry_score"
            ]
        )

    def test_asymmetry_reduces_symmetry_score(
        self,
    ) -> None:
        contacts = [
            contact(
                0,
                side="left",
                foot_x=0.00,
                foot_y=0.44,
            ),
            contact(
                1,
                side="right",
                foot_x=0.40,
                foot_y=0.56,
            ),
            contact(
                2,
                side="left",
                foot_x=1.10,
                foot_y=0.44,
            ),
            contact(
                3,
                side="right",
                foot_x=1.50,
                foot_y=0.56,
            ),
            contact(
                4,
                side="left",
                foot_x=2.20,
                foot_y=0.44,
            ),
        ]

        result = analyze_stride_geometry(
            contacts,
            context=self.context,
        )

        self.assertLess(
            result["metrics"][
                "step_length_symmetry_score"
            ],
            80.0,
        )

    def test_crossover_is_detected(
        self,
    ) -> None:
        contacts = [
            contact(
                0,
                side="left",
                foot_x=0.0,
                foot_y=0.60,
                com_y=0.50,
            ),
            contact(
                1,
                side="right",
                foot_x=0.5,
                foot_y=0.40,
                com_y=0.50,
            ),
            contact(
                2,
                side="left",
                foot_x=1.0,
                foot_y=0.62,
                com_y=0.50,
            ),
            contact(
                3,
                side="right",
                foot_x=1.5,
                foot_y=0.38,
                com_y=0.50,
            ),
        ]

        result = analyze_stride_geometry(
            contacts,
            context=self.context,
        )

        self.assertGreater(
            result["metrics"][
                "crossover_rate_percent"
            ],
            0.0,
        )

    def test_requires_minimum_contacts(
        self,
    ) -> None:
        result = analyze_stride_geometry(
            [
                contact(
                    0,
                    side="left",
                    foot_x=0.0,
                    foot_y=0.44,
                ),
                contact(
                    1,
                    side="right",
                    foot_x=0.5,
                    foot_y=0.56,
                ),
            ],
            context=self.context,
        )

        self.assertEqual(
            result["status"],
            "insufficient_data",
        )

    def test_report(
        self,
    ) -> None:
        contacts = [
            contact(
                index,
                side=(
                    "left"
                    if index % 2 == 0
                    else "right"
                ),
                foot_x=index * 0.48,
                foot_y=(
                    0.44
                    if index % 2 == 0
                    else 0.56
                ),
            )
            for index in range(6)
        ]

        result = analyze_stride_geometry(
            contacts,
            context=self.context,
            cadence_spm=280.0,
            horizontal_velocity=2.2,
        )

        report = build_stride_geometry_report(
            result
        )

        self.assertEqual(
            report["status"],
            "completed",
        )


if __name__ == "__main__":
    unittest.main()
