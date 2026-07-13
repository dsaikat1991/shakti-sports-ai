from __future__ import annotations

from statistics import mean
from typing import Any

import numpy as np

from app.services.motion.graph import MotionGraph


def summarize_graph_sequence(
    graphs: list[MotionGraph],
) -> dict[str, Any]:
    if not graphs:
        return {
            "status": "insufficient_data",
            "frames": 0,
        }

    node_counts = [
        len(graph.nodes)
        for graph in graphs
    ]

    edge_counts = [
        len(graph.edges)
        for graph in graphs
    ]

    confidences = [
        node.confidence
        for graph in graphs
        for node in graph.nodes.values()
    ]

    edge_distances = [
        edge.distance
        for graph in graphs
        for edge in graph.edges.values()
    ]

    return {
        "status": "completed",
        "frames": len(graphs),
        "average_nodes_per_frame": round(
            mean(node_counts),
            2,
        ),
        "average_edges_per_frame": round(
            mean(edge_counts),
            2,
        ),
        "average_node_confidence": (
            round(mean(confidences), 4)
            if confidences
            else None
        ),
        "edge_distance_p05": (
            round(
                float(
                    np.percentile(
                        edge_distances,
                        5,
                    )
                ),
                6,
            )
            if edge_distances
            else None
        ),
        "edge_distance_p95": (
            round(
                float(
                    np.percentile(
                        edge_distances,
                        95,
                    )
                ),
                6,
            )
            if edge_distances
            else None
        ),
    }
