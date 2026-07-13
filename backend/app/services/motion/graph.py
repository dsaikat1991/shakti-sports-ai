from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class MotionNode:
    name: str
    frame_index: int
    timestamp_ms: int
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    acceleration_x: float
    acceleration_y: float
    jerk_x: float
    jerk_y: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class MotionEdge:
    name: str
    source: str
    target: str
    distance: float
    orientation_degrees: float
    relative_velocity_x: float
    relative_velocity_y: float
    relative_acceleration_x: float
    relative_acceleration_y: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MotionGraph:
    frame_index: int
    timestamp_ms: int
    nodes: dict[str, MotionNode]
    edges: dict[str, MotionEdge]

    def get_node(self, name: str) -> MotionNode | None:
        return self.nodes.get(name)

    def get_edge(self, name: str) -> MotionEdge | None:
        return self.edges.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "timestamp_ms": self.timestamp_ms,
            "nodes": {
                name: node.to_dict()
                for name, node in self.nodes.items()
            },
            "edges": {
                name: edge.to_dict()
                for name, edge in self.edges.items()
            },
        }
