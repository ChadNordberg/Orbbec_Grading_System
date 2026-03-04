from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np


@dataclass(slots=True)
class FramePacket:
    depth_frame_mm: np.ndarray
    rgb_frame_bgr: np.ndarray
    depth_timestamp_ns: int
    rgb_timestamp_ns: int
    frame_index: int
    depth_to_rgb_transform: Any
    rgb_to_depth_transform: Any
    calibration_id: str
    camera_profile_id: str


@dataclass(slots=True)
class Track:
    unique_id: int
    state: str
    mask_centroid_history: list[tuple[float, float]] = field(default_factory=list)
    bbox_history: list[tuple[int, int, int, int]] = field(default_factory=list)
    last_seen_frame: int = -1
    missing_count: int = 0
    entered_via_entry_zone: bool = False
    has_crossed_centerline: bool = False


@dataclass(slots=True)
class ItemSample:
    unique_id: int
    sample_index: int
    frame_index: int
    length_mm: float
    width_mm: float
    height_mm: float
    volume_mm3: float
    invalid_depth_percent: float
    quality_ok: bool


@dataclass(slots=True)
class ItemRecord:
    unique_id: int
    record_number: int
    study: str
    trial: str
    plot: str
    crop: str
    variety: str
    timestamp_utc: datetime
    length_mm: float
    width_mm: float
    height_mm: float
    volume_mm3: float
    estimated_weight_g: float
    orientation_deg: float
    confidence: float
    cluster_flag: bool
    possible_cluster: bool
    image_relpath: str | None
    measurement_frame_index: int
    usable_samples: int
    invalid_depth_percent: float
    belt_speed_ft_min: float
    items_per_min: float
