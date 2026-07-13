from __future__ import annotations

from statistics import mean
from typing import Callable

from app.services.motion.graph import (
    MotionGraph,
)


def node_series(
    graphs: list[MotionGraph],
    node_name: str,
    extractor: Callable,
) -> list[tuple[int, float]]:
    result: list[tuple[int, float]] = []

    for graph in graphs:
        node = graph.get_node(node_name)

        if node is None:
            continue

        result.append(
            (
                graph.timestamp_ms,
                float(extractor(node)),
            )
        )

    return result


def edge_series(
    graphs: list[MotionGraph],
    edge_name: str,
    extractor: Callable,
) -> list[tuple[int, float]]:
    result: list[tuple[int, float]] = []

    for graph in graphs:
        edge = graph.get_edge(edge_name)

        if edge is None:
            continue

        result.append(
            (
                graph.timestamp_ms,
                float(extractor(edge)),
            )
        )

    return result


def average_node_confidence(
    graphs: list[MotionGraph],
    node_name: str,
) -> float | None:
    values = [
        graph.nodes[node_name].confidence
        for graph in graphs
        if node_name in graph.nodes
    ]

    if not values:
        return None

    return round(
        mean(values),
        4,
    )
