from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # noqa: BLE001
    yaml = None
import json


@dataclass(slots=True)
class PathsConfig:
    app: str = "app"
    config: str = "config"
    data: str = "data"
    database: str = "data/database"
    images: str = "data/images"
    calibration: str = "data/calibration"
    calibration_history: str = "data/calibration/history"
    exports: str = "data/exports"
    recordings: str = "data/recordings"
    logs: str = "logs"


@dataclass(slots=True)
class CalibrationConfig:
    calibration_id: str = "default"
    roi_depth_rect: list[int] = field(default_factory=lambda: [50, 50, 540, 420])
    centerline_x_px: int = 320
    belt_bg_depth_path: str = "data/calibration/belt_bg_depth.npy"
    homography_path: str = "data/calibration/homography.npy"


@dataclass(slots=True)
class VarietyConfig:
    name: str = "default"
    min_object_area_mm2: float = 200.0
    ignore_threshold_height_mm: float = 6.0
    measurement_sample_count_n: int = 9
    quality_invalid_depth_max_percent: float = 25.0
    quality_min_usable_samples_kmin: int = 5
    trim_count_t: int = 1


@dataclass(slots=True)
class AppSettings:
    version: str = "1.0.0"
    enable_color_metrics: bool = False
    image_saving_enabled: bool = True
    paths: PathsConfig = field(default_factory=PathsConfig)
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    default_variety: VarietyConfig = field(default_factory=VarietyConfig)


def _load_text_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _dump_text_config(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def default_settings() -> AppSettings:
    return AppSettings()


def ensure_directories(root: Path, settings: AppSettings) -> None:
    for rel in asdict(settings.paths).values():
        (root / rel).mkdir(parents=True, exist_ok=True)


def load_or_create_settings(root: Path) -> AppSettings:
    settings_path = root / "config/settings.yaml"
    if not settings_path.exists():
        settings = default_settings()
        ensure_directories(root, settings)
        save_settings(settings_path, settings)
        return settings

    raw = _load_text_config(settings_path)
    settings = AppSettings(
        version=raw.get("version", "1.0.0"),
        enable_color_metrics=raw.get("enable_color_metrics", False),
        image_saving_enabled=raw.get("image_saving_enabled", True),
        paths=PathsConfig(**raw.get("paths", {})),
        calibration=CalibrationConfig(**raw.get("calibration", {})),
        default_variety=VarietyConfig(**raw.get("default_variety", {})),
    )
    ensure_directories(root, settings)
    return settings


def save_settings(path: Path, settings: AppSettings) -> None:
    _dump_text_config(path, asdict(settings))


def snapshot_settings_dict(settings: AppSettings) -> dict[str, Any]:
    return asdict(settings)
