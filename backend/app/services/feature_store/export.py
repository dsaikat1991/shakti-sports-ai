from __future__ import annotations

import json
from pathlib import Path

from app.services.feature_store.models import (
    FeatureRecord,
)


def export_jsonl(
    records: list[FeatureRecord],
    file_path: str | Path,
) -> None:
    path = Path(file_path)

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record.to_dict(),
                    sort_keys=True,
                )
            )
            handle.write("\n")
