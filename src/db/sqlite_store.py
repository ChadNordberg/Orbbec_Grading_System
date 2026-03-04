from __future__ import annotations

import sqlite3
from pathlib import Path

from src.utils.contracts import ItemRecord, ItemSample


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    unique_id INTEGER PRIMARY KEY,
    record_number INTEGER NOT NULL,
    study TEXT, trial TEXT, plot TEXT, crop TEXT, variety TEXT,
    timestamp_utc TEXT,
    length_mm REAL, width_mm REAL, height_mm REAL, volume_mm3 REAL,
    estimated_weight_g REAL,
    orientation_deg REAL,
    confidence REAL,
    cluster_flag INTEGER,
    possible_cluster INTEGER,
    image_relpath TEXT,
    measurement_frame_index INTEGER,
    usable_samples INTEGER,
    invalid_depth_percent REAL,
    belt_speed_ft_min REAL,
    items_per_min REAL
);
CREATE TABLE IF NOT EXISTS item_samples (
    unique_id INTEGER NOT NULL,
    sample_index INTEGER NOT NULL,
    frame_index INTEGER NOT NULL,
    length_mm REAL, width_mm REAL, height_mm REAL, volume_mm3 REAL,
    invalid_depth_percent REAL,
    quality_ok INTEGER,
    PRIMARY KEY (unique_id, sample_index)
);
"""


class SQLiteStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=FULL;")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def insert_item_atomic(self, record: ItemRecord, samples: list[ItemSample]) -> None:
        cur = self.conn.cursor()
        cur.execute("BEGIN IMMEDIATE")
        cur.execute(
            """INSERT INTO items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                record.unique_id,
                record.record_number,
                record.study,
                record.trial,
                record.plot,
                record.crop,
                record.variety,
                record.timestamp_utc.isoformat(),
                record.length_mm,
                record.width_mm,
                record.height_mm,
                record.volume_mm3,
                record.estimated_weight_g,
                record.orientation_deg,
                float(record.confidence),
                int(record.cluster_flag),
                int(record.possible_cluster),
                record.image_relpath,
                record.measurement_frame_index,
                record.usable_samples,
                record.invalid_depth_percent,
                record.belt_speed_ft_min,
                record.items_per_min,
            ),
        )
        cur.executemany(
            """INSERT INTO item_samples VALUES (?,?,?,?,?,?,?,?,?)""",
            [
                (
                    s.unique_id,
                    s.sample_index,
                    s.frame_index,
                    s.length_mm,
                    s.width_mm,
                    s.height_mm,
                    s.volume_mm3,
                    s.invalid_depth_percent,
                    int(s.quality_ok),
                )
                for s in samples
            ],
        )
        self.conn.commit()
