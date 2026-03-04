from __future__ import annotations

from pathlib import Path

from PySide6 import QtWidgets

from src.ui.main_window import MainWindow
from src.utils.logging_utils import configure_logging
from src.utils.settings import load_or_create_settings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    settings = load_or_create_settings(root)
    configure_logging(root)

    app = QtWidgets.QApplication([])
    window = MainWindow(root, settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
