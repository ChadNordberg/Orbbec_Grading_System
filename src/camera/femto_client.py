from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np

from src.utils.contracts import FramePacket

logger = logging.getLogger("camera")

try:
    import pyorbbecsdk as ob  # type: ignore
except Exception:  # noqa: BLE001
    ob = None


@dataclass(slots=True)
class CameraStatus:
    connected: bool
    detail: str


class FemtoBoltClient:
    def __init__(self) -> None:
        self._connected = False
        self._frame_index = 0

    def connect(self) -> CameraStatus:
        if ob is None:
            logger.error("pyorbbecsdk unavailable.")
            self._connected = False
            return CameraStatus(False, "pyorbbecsdk unavailable")
        self._connected = True
        logger.info("Camera connected")
        return CameraStatus(True, "connected")

    def disconnect(self) -> None:
        self._connected = False

    def get_frame(self) -> FramePacket | None:
        if not self._connected:
            return None
        # Placeholder: replace with SDK frame decode path.
        depth = np.zeros((576, 640), dtype=np.float32)
        rgb = np.zeros((576, 640, 3), dtype=np.uint8)
        now = time.time_ns()
        packet = FramePacket(
            depth_frame_mm=depth,
            rgb_frame_bgr=rgb,
            depth_timestamp_ns=now,
            rgb_timestamp_ns=now,
            frame_index=self._frame_index,
            depth_to_rgb_transform=None,
            rgb_to_depth_transform=None,
            calibration_id="default",
            camera_profile_id="femto_bolt_default",
        )
        self._frame_index += 1
        return packet
