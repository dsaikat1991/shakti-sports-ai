from __future__ import annotations
from app.services.pipeline.registry import PipelineStageRegistry
def resolve_execution_order(registry:PipelineStageRegistry,requested_stages:tuple[str,...])->list[str]:
    resolved=[]; visiting=set(); visited=set()
    def visit(name:str)->None:
        if name in visited:return
        if name in visiting: raise ValueError(f"Pipeline dependency cycle detected at '{name}'.")
        stage=registry.get(name); visiting.add(name)
        for dep in stage.dependencies: visit(dep)
        visiting.remove(name); visited.add(name); resolved.append(name)
    for requested in requested_stages: visit(requested)
    return resolved
