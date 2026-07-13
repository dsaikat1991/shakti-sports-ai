from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Callable
StageHandler = Callable[["PipelineContext"], dict[str, Any]]
@dataclass(slots=True)
class PipelineContext:
    inputs: dict[str, Any]
    outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    def get_output(self, stage_name: str) -> dict[str, Any] | None:
        value=self.outputs.get(stage_name)
        return value if isinstance(value,dict) else None
@dataclass(slots=True,frozen=True)
class PipelineStage:
    name: str
    handler: StageHandler
    dependencies: tuple[str,...]=()
    cacheable: bool=True
    version: str='0.1.0'
@dataclass(slots=True,frozen=True)
class StageExecutionResult:
    stage_name: str
    status: str
    output: dict[str, Any] | None
    cached: bool
    duration_ms: float
    error: str | None=None
    def to_dict(self)->dict[str,Any]: return asdict(self)
