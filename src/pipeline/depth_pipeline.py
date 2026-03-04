from __future__ import annotations

import cv2
import numpy as np


def build_object_mask(
    depth_mm: np.ndarray,
    belt_bg_mm: np.ndarray,
    ignore_threshold_mm: float,
    min_area_px: int,
) -> np.ndarray:
    height_mm = np.clip(belt_bg_mm - depth_mm, a_min=0, a_max=None)
    mask = (height_mm > ignore_threshold_mm).astype(np.uint8)
    mask = cv2.medianBlur(mask, 3)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    out = np.zeros_like(mask)
    for idx in range(1, n_labels):
        area = stats[idx, cv2.CC_STAT_AREA]
        if area >= min_area_px:
            out[labels == idx] = 1
    return out
