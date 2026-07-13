import unittest

from app.services.physics.efficiency import (
    summarize_mechanical_efficiency,
)
from app.services.physics.energy import (
    compute_normalized_energy,
)
from app.services.physics.impulse import (
    estimate_normalized_impulse,
)
from app.services.physics.models import (
    PhysicsSample,
)
from app.services.physics.power import (
    compute_normalized_power,
)
from app.services.physics.stiffness import (
    estimate_vertical_stiffness_proxy,
)
from app.services.physics.summary import (
    build_physics_summary,
)


def sample(
    index: int,
    *,
    vx: float,
    vy: float,
    ax: float,
    ay: float,
    y: float,
) -> PhysicsSample:
    return PhysicsSample(
        frame_index=index,
        timestamp_ms=index * 100,
        com_x=index * 0.1,
        com_y=y,
        velocity_x=vx,
        velocity_y=vy,
        acceleration_x=ax,
        acceleration_y=ay,
        confidence=0.95,
    )


class TestPhysicsEngineV01(unittest.TestCase):
    def setUp(self) -> None:
        self.samples = [
            sample(
                0,
                vx=1.0,
                vy=0.0,
                ax=0.5,
                ay=0.0,
                y=0.50,
            ),
            sample(
                1,
                vx=1.1,
                vy=-0.1,
                ax=0.4,
                ay=-0.2,
                y=0.48,
            ),
            sample(
                2,
                vx=1.2,
                vy=0.1,
                ax=0.3,
                ay=0.2,
                y=0.49,
            ),
            sample(
                3,
                vx=1.3,
                vy=0.0,
                ax=0.2,
                ay=0.0,
                y=0.50,
            ),
        ]

    def test_energy_and_power_are_computed(self) -> None:
        energy = compute_normalized_energy(
            self.samples
        )

        power = compute_normalized_power(
            self.samples
        )

        self.assertEqual(
            len(energy),
            4,
        )

        self.assertEqual(
            len(power),
            4,
        )

        self.assertGreater(
            energy[1].normalized_kinetic_energy,
            0.0,
        )

    def test_impulse_proxy_is_integrated(self) -> None:
        impulse = estimate_normalized_impulse(
            self.samples,
            start_ms=0,
            end_ms=300,
        )

        self.assertIsNotNone(
            impulse,
        )

        self.assertGreater(
            impulse.normalized_horizontal_impulse,
            0.0,
        )

    def test_stiffness_proxy(self) -> None:
        result = estimate_vertical_stiffness_proxy(
            vertical_velocity_before_contact=-0.2,
            vertical_velocity_after_contact=0.3,
            vertical_com_displacement=0.04,
            contact_time_ms=120.0,
            confidence=0.9,
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertGreater(
            result[
                "normalized_vertical_stiffness"
            ],
            0.0,
        )

    def test_efficiency_and_summary(self) -> None:
        energy = compute_normalized_energy(
            self.samples
        )

        power = compute_normalized_power(
            self.samples
        )

        efficiency = (
            summarize_mechanical_efficiency(
                energy,
                power,
            )
        )

        summary = build_physics_summary(
            self.samples
        )

        self.assertEqual(
            efficiency["status"],
            "experimental",
        )

        self.assertEqual(
            summary["status"],
            "experimental",
        )


if __name__ == "__main__":
    unittest.main()
