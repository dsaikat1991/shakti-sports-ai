from __future__ import annotations
import csv, json
from pathlib import Path
from app.services.research.models import ResearchRow

def export_csv(rows: list[ResearchRow], file_path: str | Path) -> None:
    path = Path(file_path)
    fieldnames = [
        "athlete_id", "performance_id", "event", "feature_name",
        "value", "unit", "confidence", "side", "phase", "metadata",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = row.to_dict()
            payload["metadata"] = json.dumps(payload["metadata"] or {}, sort_keys=True)
            writer.writerow(payload)

def export_jsonl(rows: list[ResearchRow], file_path: str | Path) -> None:
    path = Path(file_path)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.to_dict(), sort_keys=True) + "\n")
