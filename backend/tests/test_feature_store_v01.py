import tempfile
import unittest
from pathlib import Path

from app.services.feature_store.export import (
    export_jsonl,
)
from app.services.feature_store.extractors import (
    extract_core_features,
)
from app.services.feature_store.models import (
    FeatureRecord,
    FeatureValue,
)
from app.services.feature_store.registry import (
    create_default_feature_registry,
)
from app.services.feature_store.store import (
    InMemoryFeatureStore,
)


class TestFeatureStoreV01(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = (
            create_default_feature_registry()
        )

        self.store = InMemoryFeatureStore(
            registry=self.registry
        )

    def test_write_and_query_feature(self) -> None:
        record = FeatureRecord(
            athlete_id="athlete-1",
            performance_id="performance-1",
            event="sprint",
            session_id="session-1",
            feature=FeatureValue(
                name="cadence_spm",
                value=284.0,
                unit="steps/min",
                tier="estimated",
                confidence=0.92,
                uncertainty=2.0,
                source_stage="gait",
                method="fused_gait_events",
                version="0.1.0",
            ),
        )

        self.store.write(record)

        result = self.store.query(
            performance_id="performance-1",
            feature_name="cadence_spm",
        )

        self.assertEqual(
            len(result),
            1,
        )

    def test_rejects_wrong_unit(self) -> None:
        record = FeatureRecord(
            athlete_id="athlete-1",
            performance_id="performance-1",
            event="sprint",
            session_id=None,
            feature=FeatureValue(
                name="cadence_spm",
                value=4.7,
                unit="hz",
                tier="estimated",
                confidence=0.9,
                uncertainty=None,
                source_stage="gait",
                method="test",
                version="0.1.0",
            ),
        )

        with self.assertRaises(ValueError):
            self.store.write(record)

    def test_extracts_core_features(self) -> None:
        records = extract_core_features(
            athlete_id="athlete-1",
            performance_id="performance-1",
            event="sprint",
            session_id="session-1",
            analysis={
                "biomechanics": {
                    "cadence": {
                        "cadence_steps_per_minute": 282.0,
                        "confidence": 0.91,
                    },
                    "knee_symmetry": {
                        "symmetry_score": 93.0,
                    },
                    "centre_of_mass": {
                        "vertical_oscillation_body_height_percent": 7.8,
                    },
                },
                "physics": {
                    "peak_normalized_horizontal_power": 1.72,
                    "average_confidence": 88.0,
                },
            },
        )

        self.store.write_many(
            records
        )

        self.assertEqual(
            self.store.size(),
            4,
        )

        feature_map = (
            self.store.latest_feature_map(
                performance_id="performance-1"
            )
        )

        self.assertIn(
            "cadence_spm",
            feature_map,
        )

    def test_exports_jsonl(self) -> None:
        record = FeatureRecord(
            athlete_id="athlete-1",
            performance_id="performance-1",
            event="sprint",
            session_id=None,
            feature=FeatureValue(
                name="stride_symmetry_score",
                value=94.0,
                unit="score_0_100",
                tier="estimated",
                confidence=0.9,
                uncertainty=None,
                source_stage="biomechanics",
                method="test",
                version="0.1.0",
            ),
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "features.jsonl"

            export_jsonl(
                [record],
                path,
            )

            content = path.read_text(
                encoding="utf-8"
            )

        self.assertIn(
            "stride_symmetry_score",
            content,
        )


if __name__ == "__main__":
    unittest.main()
