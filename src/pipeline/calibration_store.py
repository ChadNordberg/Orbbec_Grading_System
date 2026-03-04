from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import yaml  # type: ignore
except Exception:  # noqa: BLE001
    yaml = None


@dataclass(slots=True)
class CalibrationState:
    calibration_id: str
    roi_depth_rect: tuple[int, int, int, int]
    centerline_x_px: int
    homography: np.ndarray | None = None
    belt_bg_depth_mm: np.ndarray | None = None


def _dump(path: Path, payload: dict) -> None:
    if yaml is not None:
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def save_calibration(root: Path, cal: CalibrationState) -> None:
    cal_dir = root / "data/calibration"
    hist_dir = root / "data/calibration/history"
    cal_dir.mkdir(parents=True, exist_ok=True)
    hist_dir.mkdir(parents=True, exist_ok=True)

    yml_path = cal_dir / "calibration.yaml"
    if yml_path.exists():
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        yml_path.replace(hist_dir / f"calibration_{ts}.yaml")

    if cal.homography is not None:
        np.save(cal_dir / "homography.npy", cal.homography)
    if cal.belt_bg_depth_mm is not None:
        np.save(cal_dir / "belt_bg_depth.npy", cal.belt_bg_depth_mm)

    payload = asdict(cal)
    payload["homography"] = str((cal_dir / "homography.npy").as_posix()) if cal.homography is not None else None
    payload["belt_bg_depth_mm"] = str((cal_dir / "belt_bg_depth.npy").as_posix()) if cal.belt_bg_depth_mm is not None else None
    _dump(yml_path, payload)


def load_calibration(root: Path) -> CalibrationState | None:
    yml_path = root / "data/calibration/calibration.yaml"
    if not yml_path.exists():
        return None
    raw = _load(yml_path)
    homography = np.load(root / "data/calibration/homography.npy") if (root / "data/calibration/homography.npy").exists() else None
    belt = np.load(root / "data/calibration/belt_bg_depth.npy") if (root / "data/calibration/belt_bg_depth.npy").exists() else None
    return CalibrationState(
        calibration_id=raw["calibration_id"],
        roi_depth_rect=tuple(raw["roi_depth_rect"]),
        centerline_x_px=raw["centerline_x_px"],
        homography=homography,
        belt_bg_depth_mm=belt,
    )
