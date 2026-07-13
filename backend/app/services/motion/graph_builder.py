from __future__ import annotations

import math
from collections import defaultdict

from app.services.motion.graph import (
    MotionEdge,
    MotionGraph,
    MotionNode,
)
from app.services.motion.models import PointMotionState


DEFAULT_EDGES: tuple[tuple[str, str, str], ...] = (
    ("left_upper_arm", "left_shoulder", "left_elbow"),
    ("left_forearm", "left_elbow", "left_wrist"),
    ("right_upper_arm", "right_shoulder", "right_elbow"),
    ("right_forearm", "right_elbow", "right_wrist"),
    ("left_thigh", "left_hip", "left_knee"),
    ("left_shank", "left_knee", "left_ankle"),
    ("left_foot", "left_ankle", "left_toe"),
    ("right_thigh", "right_hip", "right_knee"),
    ("right_shank", "right_knee", "right_ankle"),
    ("right_foot", "right_ankle", "right_toe"),
    ("shoulder_line", "left_shoulder", "right_shoulder"),
    ("pelvis_line", "left_hip", "right_hip"),
    ("left_torso", "left_shoulder", "left_hip"),
    ("right_torso", "right_shoulder", "right_hip"),
)


def _build_node(
    name: str,
    state: PointMotionState,
) -> MotionNode:
    return MotionNode(
        name=name,
        frame_index=state.frame_index,
        timestamp_ms=state.timestamp_ms,
        x=state.x,
        y=state.y,
        velocity_x=state.velocity_x,
        velocity_y=state.velocity_y,
        acceleration_x=state.acceleration_x,
        acceleration_y=state.acceleration_y,
        jerk_x=state.jerk_x,
        jerk_y=state.jerk_y,
        confidence=state.confidence,
    )


def _build_edge(
    name: str,
    source: MotionNode,
    target: MotionNode,
) -> MotionEdge:
    dx = target.x - source.x
    dy = target.y - source.y

    return MotionEdge(
        name=name,
        source=source.name,
        target=target.name,
        distance=round(
            (dx**2 + dy**2) ** 0.5,
            6,
        ),
        orientation_degrees=round(
            math.degrees(
                math.atan2(dy, dx)
            ),
            6,
        ),
        relative_velocity_x=round(
            target.velocity_x
            - source.velocity_x,
            6,
        ),
        relative_velocity_y=round(
            target.velocity_y
            - source.velocity_y,
            6,
        ),
        relative_acceleration_x=round(
            target.acceleration_x
            - source.acceleration_x,
            6,
        ),
        relative_acceleration_y=round(
            target.acceleration_y
            - source.acceleration_y,
            6,
        ),
        confidence=round(
            min(
                source.confidence,
                target.confidence,
            ),
            4,
        ),
    )


def build_motion_graphs(
    motion_series: dict[
        str,
        list[PointMotionState],
    ],
    *,
    edge_definitions: tuple[
        tuple[str, str, str],
        ...
    ] = DEFAULT_EDGES,
) -> list[MotionGraph]:
    by_timestamp: dict[
        int,
        dict[str, PointMotionState],
    ] = defaultdict(dict)

    for name, states in motion_series.items():
        for state in states:
            by_timestamp[
                state.timestamp_ms
            ][name] = state

    graphs: list[MotionGraph] = []

    for timestamp_ms in sorted(by_timestamp):
        states = by_timestamp[timestamp_ms]

        if not states:
            continue

        nodes = {
            name: _build_node(name, state)
            for name, state in states.items()
        }

        frame_index = min(
            state.frame_index
            for state in states.values()
        )

        edges: dict[str, MotionEdge] = {}

        for edge_name, source_name, target_name in edge_definitions:
            source = nodes.get(source_name)
            target = nodes.get(target_name)

            if source is None or target is None:
                continue

            edges[edge_name] = _build_edge(
                edge_name,
                source,
                target,
            )

        graphs.append(
            MotionGraph(
                frame_index=frame_index,
                timestamp_ms=timestamp_ms,
                nodes=nodes,
                edges=edges,
            )
        )

    return graphs
