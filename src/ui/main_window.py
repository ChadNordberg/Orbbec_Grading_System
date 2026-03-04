from __future__ import annotations

import queue
import threading
from pathlib import Path

import cv2
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

from src.camera.acquisition import AcquisitionWorker
from src.pipeline.calibration_store import CalibrationState, load_calibration, save_calibration
from src.utils.contracts import FramePacket
from src.utils.settings import AppSettings, save_settings


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, root: Path, settings: AppSettings) -> None:
        super().__init__()
        self.root = root
        self.settings = settings
        self.setWindowTitle("Femto Bolt Conveyor Commodity Measurement")
        self.resize(1280, 800)

        self.queue: queue.Queue[FramePacket] = queue.Queue(maxsize=30)
        self.stop_event = threading.Event()
        self.worker = AcquisitionWorker(self.queue, self.stop_event)
        self.thread = threading.Thread(target=self.worker.run, daemon=True)

        self.current_frame: FramePacket | None = None
        self.show_depth = False

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QGridLayout(central)

        self.live_label = QtWidgets.QLabel("No stream")
        self.live_label.setMinimumSize(840, 600)
        self.live_label.setStyleSheet("background: #111; color: #ddd")
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["UniqueID", "L", "W", "H", "V", "Conf"])

        controls = QtWidgets.QHBoxLayout()
        self.btn_start = QtWidgets.QPushButton("Start Grading")
        self.btn_stop = QtWidgets.QPushButton("Stop Grading")
        self.btn_capture_belt = QtWidgets.QPushButton("Calibrate Belt Plane")
        self.btn_toggle_depth = QtWidgets.QPushButton("Depth Toggle")
        self.btn_export = QtWidgets.QPushButton("Export Database")
        for b in [self.btn_start, self.btn_stop, self.btn_capture_belt, self.btn_toggle_depth, self.btn_export]:
            controls.addWidget(b)

        self.status_label = QtWidgets.QLabel("Idle")

        layout.addWidget(self.live_label, 0, 0)
        layout.addWidget(self.table, 0, 1)
        layout.addLayout(controls, 1, 0, 1, 2)
        layout.addWidget(self.status_label, 2, 0, 1, 2)

        self.btn_start.clicked.connect(self.start_stream)
        self.btn_stop.clicked.connect(self.stop_stream)
        self.btn_toggle_depth.clicked.connect(self._toggle_depth)
        self.btn_capture_belt.clicked.connect(self.capture_belt_map)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.poll_frame)
        self.timer.start(33)

        self.calibration = load_calibration(self.root)

    def start_stream(self) -> None:
        if not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.worker.run, daemon=True)
            self.thread.start()
            self.status_label.setText("Streaming")

    def stop_stream(self) -> None:
        self.stop_event.set()
        self.status_label.setText("Stopped")

    def _toggle_depth(self) -> None:
        self.show_depth = not self.show_depth

    def poll_frame(self) -> None:
        try:
            self.current_frame = self.queue.get_nowait()
        except queue.Empty:
            return

        roi = self.settings.calibration.roi_depth_rect
        x, y, w, h = roi

        if self.show_depth:
            depth = self.current_frame.depth_frame_mm.copy()
            norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            img = cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)
        else:
            img = self.current_frame.rgb_frame_bgr.copy()

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_BGR888)
        pix = QtGui.QPixmap.fromImage(qimg).scaled(self.live_label.size(), QtCore.Qt.KeepAspectRatio)
        self.live_label.setPixmap(pix)

    def capture_belt_map(self) -> None:
        if self.current_frame is None:
            self.status_label.setText("No frame for belt map")
            return
        x, y, w, h = self.settings.calibration.roi_depth_rect
        belt = self.current_frame.depth_frame_mm[y : y + h, x : x + w].copy()
        cal = CalibrationState(
            calibration_id=self.settings.calibration.calibration_id,
            roi_depth_rect=tuple(self.settings.calibration.roi_depth_rect),
            centerline_x_px=self.settings.calibration.centerline_x_px,
            homography=np.eye(3, dtype=np.float32),
            belt_bg_depth_mm=belt,
        )
        save_calibration(self.root, cal)
        save_settings(self.root / "config/settings.yaml", self.settings)
        self.status_label.setText("Belt map captured")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: N802
        self.stop_event.set()
        return super().closeEvent(event)
