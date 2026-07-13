import unittest
from app.services.pipeline.cache import PipelineCache
from app.services.pipeline.dependency_graph import resolve_execution_order
from app.services.pipeline.models import PipelineStage
from app.services.pipeline.pipeline import PipelineOrchestrator
from app.services.pipeline.registry import PipelineStageRegistry
from app.services.pipeline.stages import create_default_pipeline_registry
class TestPipelineOrchestratorV01(unittest.TestCase):
    def test_resolves_dependencies(self):
        order=resolve_execution_order(create_default_pipeline_registry(),('report',))
        self.assertEqual(order[0],'pose'); self.assertEqual(order[-1],'report'); self.assertIn('athletics',order)
    def test_runs_requested_stage_and_dependencies(self):
        registry=PipelineStageRegistry()
        registry.register(PipelineStage('first',lambda c:{'value':2}))
        registry.register(PipelineStage('second',lambda c:{'value':c.outputs['first']['value']*3},('first',)))
        result=PipelineOrchestrator(registry=registry).run(inputs={},requested_stages=('second',))
        self.assertEqual(result['requested_outputs']['second']['value'],6)
        self.assertEqual(result['execution_order'],['first','second'])
    def test_cache_is_used(self):
        calls={'count':0}
        def handler(context): calls['count']+=1; return {'value':10}
        registry=PipelineStageRegistry(); registry.register(PipelineStage('cached',handler))
        pipeline=PipelineOrchestrator(registry=registry,cache=PipelineCache())
        first=pipeline.run(inputs={'id':1},requested_stages=('cached',))
        second=pipeline.run(inputs={'id':1},requested_stages=('cached',))
        self.assertEqual(calls['count'],1); self.assertFalse(first['stages'][0]['cached']); self.assertTrue(second['stages'][0]['cached'])
    def test_cycle_is_rejected(self):
        registry=PipelineStageRegistry(); registry.register(PipelineStage('a',lambda c:{},('b',))); registry.register(PipelineStage('b',lambda c:{},('a',)))
        with self.assertRaises(ValueError): resolve_execution_order(registry,('a',))
if __name__=='__main__': unittest.main()
