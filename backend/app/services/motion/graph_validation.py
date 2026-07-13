from __future__ import annotations

from typing import Any

from app.services.motion.graph import MotionGraph


def validate_motion_graph(
    graph: MotionGraph,
    *,
    minimum_node_confidence: float = 0.50,
    maximum_edge_length: float = 1.50,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    for name, node in graph.nodes.items():
        if not 0.0 <= node.x <= 1.0:
            issues.append(
                {
                    "type": "node_out_of_bounds",
                    "node": name,
                    "axis": "x",
                    "value": node.x,
                }
            )

        if not 0.0 <= node.y <= 1.0:
            issues.append(
                {
                    "type": "node_out_of_bounds",
                    "node": name,
                    "axis": "y",
                    "value": node.y,
                }
            )

        if node.confidence < minimum_node_confidence:
            issues.append(
                {
                    "type": "low_node_confidence",
                    "node": name,
                    "value": node.confidence,
                }
            )

    for name, edge in graph.edges.items():
        if edge.distance <= 0.0:
            issues.append(
                {
                    "type": "invalid_edge_length",
                    "edge": name,
                    "value": edge.distance,
                }
            )

        elif edge.distance > maximum_edge_length:
            issues.append(
                {
                    "type": "implausible_edge_length",
                    "edge": name,
                    "value": edge.distance,
                }
            )

    return {
        "valid": not issues,
        "issue_count": len(issues),
        "issues": issues,
    }


def validate_graph_sequence(
    graphs: list[MotionGraph],
) -> dict[str, Any]:
    results = [
        validate_motion_graph(graph)
        for graph in graphs
    ]

    invalid_frames = sum(
        1
        for result in results
        if not result["valid"]
    )

    return {
        "status": (
            "completed"
            if graphs
            else "insufficient_data"
        ),
        "frames": len(graphs),
        "invalid_frames": invalid_frames,
        "valid_frame_percent": (
            round(
                (
                    len(graphs)
                    - invalid_frames
                )
                / len(graphs)
                * 100.0,
                2,
            )
            if graphs
            else None
        ),
        "frame_results": results,
    }
