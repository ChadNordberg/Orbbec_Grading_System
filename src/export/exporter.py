from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # noqa: BLE001
    yaml = None


def export_items(db_path: Path, export_dir: Path, settings_snapshot: dict) -> tuple[Path, Path]:
    export_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = export_dir / f"export_{ts}.csv"
    yml_path = export_dir / f"export_{ts}_config.yaml"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM items ORDER BY unique_id")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(cols)
        writer.writerows(rows)

    if yaml is not None:
        yml_path.write_text(yaml.safe_dump(settings_snapshot, sort_keys=False), encoding="utf-8")
    else:
        yml_path.write_text(json.dumps(settings_snapshot, indent=2), encoding="utf-8")

    return csv_path, yml_path
