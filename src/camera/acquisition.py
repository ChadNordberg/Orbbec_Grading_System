from __future__ import annotations

import logging
import queue
import threading
import time

from src.camera.femto_client import FemtoBoltClient
from src.utils.contracts import FramePacket

logger = logging.getLogger(__name__)


class AcquisitionWorker:
    def __init__(self, out_queue: queue.Queue[FramePacket], stop_event: threading.Event) -> None:
        self.out_queue = out_queue
        self.stop_event = stop_event
        self.client = FemtoBoltClient()

    def run(self) -> None:
        status = self.client.connect()
        if not status.connected:
            logger.error("Camera connect failed: %s", status.detail)
            return

        while not self.stop_event.is_set():
            frame = self.client.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            try:
                self.out_queue.put(frame, timeout=0.1)
            except queue.Full:
                logger.warning("Frame queue full; dropping frame %s", frame.frame_index)

        self.client.disconnect()
