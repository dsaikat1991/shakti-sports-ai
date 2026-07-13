import unittest
from app.services.talent.benchmarking import benchmark_profile, percentile_rank
from app.services.talent.cohorts import filter_cohort
from app.services.talent.engine import analyze_similarity_and_benchmark
from app.services.talent.models import AthleteProfileVector
from app.services.talent.similarity import find_similar_athletes

def profile(athlete_id,*,efficiency,contact,cadence,symmetry,age_group="U18",sex="male",level="district"):
    return AthleteProfileVector(athlete_id,"sprint",age_group,sex,level,{"mechanical_efficiency_score":efficiency,"ground_contact_ms":contact,"cadence_spm":cadence,"symmetry_score":symmetry},{"mechanical_efficiency_score":0.92,"ground_contact_ms":0.90,"cadence_spm":0.91,"symmetry_score":0.89})

class TestSimilarityBenchmarkEngineV01(unittest.TestCase):
    def setUp(self):
        self.target=profile("target",efficiency=86,contact=116,cadence=286,symmetry=92)
        self.population=[profile("a1",efficiency=85,contact=118,cadence=284,symmetry=91),profile("a2",efficiency=72,contact=138,cadence=270,symmetry=80),profile("a3",efficiency=88,contact=114,cadence=288,symmetry=93,level="national"),profile("a4",efficiency=90,contact=110,cadence=292,symmetry=95,age_group="U20")]
    def test_percentile_direction(self):
        self.assertEqual(percentile_rank(value=90,cohort_values=[70,80,90],lower_is_better=False),100.0)
        self.assertEqual(percentile_rank(value=100,cohort_values=[100,120,140],lower_is_better=True),100.0)
    def test_cohort_filtering(self): self.assertEqual(len(filter_cohort(self.population,event="sprint",age_group="U18",sex="male")),3)
    def test_benchmark_output(self):
        result=benchmark_profile(self.target,filter_cohort(self.population,event="sprint",age_group="U18",sex="male")); self.assertEqual(result["status"],"completed"); self.assertGreater(len(result["metrics"]),0)
    def test_similarity_ranks_close_profile_first(self):
        result=find_similar_athletes(self.target,filter_cohort(self.population,event="sprint",age_group="U18",sex="male"),minimum_shared_features=3)
        self.assertEqual(result["status"],"completed"); self.assertIn(result["matches"][0]["athlete_id"],{"a1","a3"})
    def test_full_engine(self):
        result=analyze_similarity_and_benchmark(target=self.target,population=self.population,same_age_group=True,same_sex=True,top_k=3)
        self.assertEqual(result["status"],"completed"); self.assertEqual(result["cohort_definition"]["cohort_size"],3); self.assertEqual(result["validation_level"],"experimental")

if __name__=="__main__": unittest.main()
