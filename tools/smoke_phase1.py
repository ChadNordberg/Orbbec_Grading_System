from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.settings import load_or_create_settings


if __name__ == "__main__":
    s = load_or_create_settings(ROOT)
    print("settings_loaded", s.calibration.roi_depth_rect)
