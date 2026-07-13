from __future__ import annotations
from time import perf_counter
from typing import Any
from app.services.pipeline.cache import PipelineCache
from app.services.pipeline.dependency_graph import resolve_execution_order
from app.services.pipeline.models import PipelineContext, StageExecutionResult
from app.services.pipeline.registry import PipelineStageRegistry
class PipelineExecutionError(RuntimeError): pass
class PipelineOrchestrator:
    def __init__(self,*,registry:PipelineStageRegistry,cache:PipelineCache|None=None,fail_fast:bool=True)->None:
        self.registry=registry; self.cache=cache or PipelineCache(); self.fail_fast=fail_fast
    def _cache_payload(self,*,stage_name:str,context:PipelineContext)->dict[str,Any]:
        stage=self.registry.get(stage_name)
        return {'inputs':context.inputs,'dependencies':{d:context.outputs.get(d) for d in stage.dependencies}}
    def run(self,*,inputs:dict[str,Any],requested_stages:tuple[str,...],metadata:dict[str,Any]|None=None)->dict[str,Any]:
        context=PipelineContext(inputs=dict(inputs),metadata=dict(metadata or {}))
        order=resolve_execution_order(self.registry,requested_stages)
        results=[]
        for stage_name in order:
            stage=self.registry.get(stage_name)
            key=self.cache.build_key(stage_name=stage.name,stage_version=stage.version,payload=self._cache_payload(stage_name=stage_name,context=context))
            cached=self.cache.get(key) if stage.cacheable else None
            if cached is not None:
                context.outputs[stage_name]=cached; results.append(StageExecutionResult(stage_name,'completed',cached,True,0.0)); continue
            started=perf_counter()
            try:
                output=stage.handler(context)
                if not isinstance(output,dict): raise TypeError(f"Stage '{stage_name}' must return a dictionary.")
                duration=(perf_counter()-started)*1000.0
                context.outputs[stage_name]=output
                if stage.cacheable:self.cache.set(key,output)
                results.append(StageExecutionResult(stage_name,'completed',output,False,round(duration,3)))
            except Exception as exc:
                duration=(perf_counter()-started)*1000.0
                results.append(StageExecutionResult(stage_name,'failed',None,False,round(duration,3),f"{type(exc).__name__}: {exc}"))
                if self.fail_fast: raise PipelineExecutionError(f"Pipeline failed at stage '{stage_name}'.") from exc
        return {'status':'completed' if all(r.status=='completed' for r in results) else 'partial','execution_order':order,'requested_outputs':{s:context.outputs.get(s) for s in requested_stages},'all_outputs':context.outputs,'stages':[r.to_dict() for r in results],'metadata':context.metadata}
