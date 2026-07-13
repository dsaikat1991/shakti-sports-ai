import tempfile
import unittest
from pathlib import Path

from app.services.research.cohort import build_cohort
from app.services.research.comparisons import compare_feature
from app.services.research.datasets import ResearchDataset
from app.services.research.exports import export_csv, export_jsonl
from app.services.research.models import CohortDefinition, ResearchRow
from app.services.research.statistics import bland_altman, pearson_correlation

def row(athlete, performance, value, level):
    return ResearchRow(
        athlete_id=athlete,
        performance_id=performance,
        event="sprint",
        feature_name="cadence_spm",
        value=value,
        unit="steps/min",
        confidence=0.92,
        metadata={"level": level},
    )

class TestResearchEngineV01(unittest.TestCase):
    def setUp(self):
        self.rows = [
            row("a1", "p1", 280.0, "district"),
            row("a2", "p2", 284.0, "district"),
            row("a3", "p3", 292.0, "national"),
            row("a4", "p4", 296.0, "national"),
        ]

    def test_dataset_and_cohort(self):
        dataset = ResearchDataset(self.rows)
        cohort = build_cohort(
            dataset.rows(),
            CohortDefinition("national", {"metadata__level": "national"}),
        )
        self.assertEqual(dataset.size(), 4)
        self.assertEqual(len(cohort), 2)

    def test_comparison(self):
        district = build_cohort(
            self.rows,
            CohortDefinition("district", {"metadata__level": "district"}),
        )
        national = build_cohort(
            self.rows,
            CohortDefinition("national", {"metadata__level": "national"}),
        )
        result = compare_feature(
            feature_name="cadence_spm",
            cohort_a_name="district",
            cohort_a_rows=district,
            cohort_b_name="national",
            cohort_b_rows=national,
        )
        self.assertIsNotNone(result.statistics["mean_difference"])

    def test_statistics(self):
        self.assertIsNotNone(pearson_correlation([1,2,3], [2,4,6]))
        result = bland_altman([10,11,12], [9,10,11])
        self.assertEqual(result["status"], "completed")

    def test_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "research.csv"
            jsonl_path = Path(directory) / "research.jsonl"
            export_csv(self.rows, csv_path)
            export_jsonl(self.rows, jsonl_path)
            self.assertIn("cadence_spm", csv_path.read_text(encoding="utf-8"))
            self.assertIn("cadence_spm", jsonl_path.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
