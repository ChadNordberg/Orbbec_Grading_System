from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(root: Path) -> None:
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    system_log = logs_dir / "system.log"
    camera_log = logs_dir / "camera.log"

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    h1 = logging.FileHandler(system_log, encoding="utf-8")
    h1.setFormatter(fmt)
    root_logger.addHandler(h1)

    cam_logger = logging.getLogger("camera")
    cam_logger.setLevel(logging.INFO)
    cam_logger.handlers.clear()
    h2 = logging.FileHandler(camera_log, encoding="utf-8")
    h2.setFormatter(fmt)
    cam_logger.addHandler(h2)
