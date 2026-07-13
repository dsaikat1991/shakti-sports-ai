from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.pose_remote.client import RTMPoseWorkerClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--runs", type=int, default=10)
    args = parser.parse_args()

    client = RTMPoseWorkerClient()
    client.initialize()
    times = []
    for _ in range(args.runs):
        result = client.infer_image_file(args.image)
        times.append(float(result["inference_ms"]))

    average_ms = mean(times)
    print(f"Runs: {args.runs}")
    print(f"Average inference: {average_ms:.2f} ms")
    print(f"Approximate model FPS: {1000.0 / average_ms:.2f}")


if __name__ == "__main__":
    main()
