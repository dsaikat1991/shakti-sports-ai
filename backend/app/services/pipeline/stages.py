from __future__ import annotations
from typing import Any
from app.services.pipeline.models import PipelineContext, PipelineStage
from app.services.pipeline.registry import PipelineStageRegistry
def create_default_pipeline_registry()->PipelineStageRegistry:
    registry=PipelineStageRegistry()
    def pose_handler(context:PipelineContext)->dict[str,Any]:
        return {'status':'ready_for_integration','video_path':context.inputs.get('video_path')}
    def dependency_summary(stage_name:str):
        def handler(context:PipelineContext)->dict[str,Any]:
            return {'status':'ready_for_integration','stage':stage_name,'dependencies':{k:context.outputs.get(k) for k in context.outputs}}
        return handler
    registry.register(PipelineStage('pose',pose_handler,version='1.0.0'))
    registry.register(PipelineStage('motion',dependency_summary('motion'),('pose',),True,'1.0.0'))
    registry.register(PipelineStage('motion_graph',dependency_summary('motion_graph'),('motion',),True,'1.0.0'))
    registry.register(PipelineStage('gait',dependency_summary('gait'),('motion','motion_graph'),True,'0.3.0'))
    registry.register(PipelineStage('physics',dependency_summary('physics'),('motion','motion_graph'),True,'0.1.0'))
    registry.register(PipelineStage('athletics',dependency_summary('athletics'),('gait','physics'),True,'0.2.0'))
    registry.register(PipelineStage('validation',dependency_summary('validation'),('athletics',),True,'0.1.0'))
    registry.register(PipelineStage('report',dependency_summary('report'),('validation',),False,'0.1.0'))
    return registry
