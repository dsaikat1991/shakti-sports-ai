import unittest

from app.services.motion.graph_builder import (
    build_motion_graphs,
)
from app.services.motion.graph_queries import (
    average_node_confidence,
    edge_series,
    node_series,
)
from app.services.motion.graph_statistics import (
    summarize_graph_sequence,
)
from app.services.motion.graph_validation import (
    validate_graph_sequence,
)
from app.services.motion.models import (
    PointMotionState,
)


def state(
    frame: int,
    timestamp: int,
    x: float,
    y: float,
) -> PointMotionState:
    return PointMotionState(
        frame_index=frame,
        timestamp_ms=timestamp,
        x=x,
        y=y,
        velocity_x=1.0,
        velocity_y=0.5,
        speed=1.118,
        acceleration_x=0.1,
        acceleration_y=0.2,
        acceleration_magnitude=0.224,
        jerk_x=0.01,
        jerk_y=0.02,
        jerk_magnitude=0.022,
        confidence=0.95,
    )


class TestMotionGraphV2(unittest.TestCase):
    def setUp(self) -> None:
        self.series = {
            "left_hip": [
                state(0, 0, 0.3, 0.5),
                state(1, 100, 0.4, 0.5),
            ],
            "left_knee": [
                state(0, 0, 0.4, 0.7),
                state(1, 100, 0.5, 0.7),
            ],
        }

    def test_builds_nodes_and_edges(self) -> None:
        graphs = build_motion_graphs(
            self.series,
            edge_definitions=(
                (
                    "left_thigh",
                    "left_hip",
                    "left_knee",
                ),
            ),
        )

        self.assertEqual(len(graphs), 2)
        self.assertIn(
            "left_thigh",
            graphs[0].edges,
        )

    def test_queries_work(self) -> None:
        graphs = build_motion_graphs(
            self.series,
            edge_definitions=(
                (
                    "left_thigh",
                    "left_hip",
                    "left_knee",
                ),
            ),
        )

        node_values = node_series(
            graphs,
            "left_hip",
            lambda node: node.x,
        )

        edge_values = edge_series(
            graphs,
            "left_thigh",
            lambda edge: edge.distance,
        )

        self.assertEqual(len(node_values), 2)
        self.assertEqual(len(edge_values), 2)
        self.assertEqual(
            average_node_confidence(
                graphs,
                "left_hip",
            ),
            0.95,
        )

    def test_statistics_and_validation(self) -> None:
        graphs = build_motion_graphs(
            self.series,
            edge_definitions=(
                (
                    "left_thigh",
                    "left_hip",
                    "left_knee",
                ),
            ),
        )

        summary = summarize_graph_sequence(
            graphs
        )

        validation = validate_graph_sequence(
            graphs
        )

        self.assertEqual(
            summary["status"],
            "completed",
        )

        self.assertEqual(
            validation["invalid_frames"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
