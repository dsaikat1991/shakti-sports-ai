from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.pose_remote.client import RTMPoseWorkerClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    args = parser.parse_args()

    client = RTMPoseWorkerClient()
    print(client.health())
    print(client.initialize())
    result = client.infer_image_file(args.image)
    print(
        {
            "status": result["status"],
            "model": result["model_name"],
            "device": result["device"],
            "inference_ms": result["inference_ms"],
            "people": len(result["instances"]),
            "landmarks_first_person": (
                len(result["instances"][0]["keypoints"])
                if result["instances"]
                else 0
            ),
            "warnings": result.get("warnings", []),
        }
    )


if __name__ == "__main__":
    main()
