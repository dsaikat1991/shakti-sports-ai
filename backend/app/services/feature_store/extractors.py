from __future__ import annotations

from typing import Any

from app.services.feature_store.models import (
    FeatureRecord,
    FeatureValue,
)


def _feature(
    *,
    athlete_id: str | None,
    performance_id: str,
    event: str,
    session_id: str | None,
    name: str,
    value: float | int | str | bool | None,
    unit: str | None,
    tier: str,
    confidence: float | None,
    uncertainty: float | None,
    source_stage: str,
    method: str,
    version: str,
    side: str | None = None,
    phase: str | None = None,
) -> FeatureRecord:
    return FeatureRecord(
        athlete_id=athlete_id,
        performance_id=performance_id,
        event=event,
        session_id=session_id,
        feature=FeatureValue(
            name=name,
            value=value,
            unit=unit,
            tier=tier,
            confidence=confidence,
            uncertainty=uncertainty,
            source_stage=source_stage,
            method=method,
            version=version,
            side=side,
            phase=phase,
        ),
    )


def extract_core_features(
    *,
    athlete_id: str | None,
    performance_id: str,
    event: str,
    session_id: str | None,
    analysis: dict[str, Any],
) -> list[FeatureRecord]:
    records: list[FeatureRecord] = []

    biomechanics = analysis.get(
        "biomechanics",
        {}
    )

    cadence = biomechanics.get(
        "cadence",
        {}
    )

    cadence_value = cadence.get(
        "cadence_steps_per_minute"
    )

    if isinstance(cadence_value, (int, float)):
        records.append(
            _feature(
                athlete_id=athlete_id,
                performance_id=performance_id,
                event=event,
                session_id=session_id,
                name="cadence_spm",
                value=float(cadence_value),
                unit="steps/min",
                tier="estimated",
                confidence=(
                    float(cadence.get("confidence"))
                    if isinstance(
                        cadence.get("confidence"),
                        (int, float),
                    )
                    else None
                ),
                uncertainty=None,
                source_stage="gait",
                method="fused_gait_events",
                version="0.1.0",
            )
        )

    symmetry = biomechanics.get(
        "knee_symmetry",
        {}
    )

    symmetry_score = symmetry.get(
        "symmetry_score"
    )

    if isinstance(symmetry_score, (int, float)):
        records.append(
            _feature(
                athlete_id=athlete_id,
                performance_id=performance_id,
                event=event,
                session_id=session_id,
                name="stride_symmetry_score",
                value=float(symmetry_score),
                unit="score_0_100",
                tier="estimated",
                confidence=None,
                uncertainty=None,
                source_stage="biomechanics",
                method="left_right_range_comparison",
                version="0.1.0",
            )
        )

    com = biomechanics.get(
        "centre_of_mass",
        {}
    )

    oscillation = com.get(
        "vertical_oscillation_body_height_percent"
    )

    if isinstance(oscillation, (int, float)):
        records.append(
            _feature(
                athlete_id=athlete_id,
                performance_id=performance_id,
                event=event,
                session_id=session_id,
                name="vertical_oscillation_body_height_percent",
                value=float(oscillation),
                unit="percent",
                tier="estimated",
                confidence=None,
                uncertainty=None,
                source_stage="biomechanics",
                method="weighted_pose_landmark_centre_proxy",
                version="0.1.0",
            )
        )

    physics = analysis.get(
        "physics",
        {}
    )

    peak_power = physics.get(
        "peak_normalized_horizontal_power"
    )

    if isinstance(peak_power, (int, float)):
        records.append(
            _feature(
                athlete_id=athlete_id,
                performance_id=performance_id,
                event=event,
                session_id=session_id,
                name="peak_normalized_horizontal_power",
                value=float(peak_power),
                unit="normalized",
                tier="estimated",
                confidence=(
                    float(physics.get("average_confidence")) / 100.0
                    if isinstance(
                        physics.get("average_confidence"),
                        (int, float),
                    )
                    else None
                ),
                uncertainty=None,
                source_stage="physics",
                method="normalized_com_acceleration_velocity_proxy",
                version="0.1.0",
            )
        )

    return records
