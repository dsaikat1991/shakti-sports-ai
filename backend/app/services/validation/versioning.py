from __future__ import annotations
from typing import Any
DEFAULT_ENGINE_VERSIONS={"platform_version":"0.1.0","motion_engine":"1.0.0","motion_graph":"1.0.0","physics_engine":"0.1.0","validation_engine":"0.1.0","sprint_engine":"0.2.0","pose_adapter":"1.0.0","analysis_standard":"Shakti Athletics Standard 2026.1"}
def build_version_registry(overrides:dict[str,str]|None=None)->dict[str,Any]:
    versions=dict(DEFAULT_ENGINE_VERSIONS)
    if overrides: versions.update(overrides)
    return {"status":"versioned","components":versions}
