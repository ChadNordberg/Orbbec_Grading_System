from __future__ import annotations

import numpy as np

from src.utils.contracts import ItemSample


def trimmed_mean(values: list[float], trim: int) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    if len(arr) <= 2 * trim:
        return float(np.median(arr))
    return float(np.mean(arr[trim:-trim]))


def finalize_samples(samples: list[ItemSample], n: int, trim: int, invalid_max: float, kmin: int) -> dict[str, float]:
    usable = [s for s in samples if s.invalid_depth_percent <= invalid_max]
    if len(usable) < kmin:
        usable = samples
    conf = max(0.0, min(1.0, (len(usable) / max(1, n)) * (1.0 - np.mean([s.invalid_depth_percent for s in usable]) / 100.0)))
    return {
        "length_mm": trimmed_mean([s.length_mm for s in usable], trim),
        "width_mm": trimmed_mean([s.width_mm for s in usable], trim),
        "height_mm": trimmed_mean([s.height_mm for s in usable], trim),
        "volume_mm3": trimmed_mean([s.volume_mm3 for s in usable], trim),
        "confidence": conf,
        "usable_samples": float(len(usable)),
    }
