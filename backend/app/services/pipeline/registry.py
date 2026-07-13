from __future__ import annotations
from app.services.pipeline.models import PipelineStage
class PipelineStageRegistry:
    def __init__(self)->None: self._stages: dict[str,PipelineStage]={}
    def register(self,stage:PipelineStage)->None:
        if stage.name in self._stages: raise ValueError(f"Pipeline stage '{stage.name}' is already registered.")
        self._stages[stage.name]=stage
    def replace(self,stage:PipelineStage)->None: self._stages[stage.name]=stage
    def get(self,stage_name:str)->PipelineStage:
        try:return self._stages[stage_name]
        except KeyError as exc: raise KeyError(f"Pipeline stage '{stage_name}' is not registered.") from exc
    def has(self,stage_name:str)->bool:return stage_name in self._stages
    def names(self)->tuple[str,...]:return tuple(sorted(self._stages))
