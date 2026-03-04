# Femto Bolt Conveyor Commodity Measurement System

Local-first Windows 11 desktop app for Orbbec Femto Bolt grading workflows.

## Setup
1. Install Python 3.11.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Orbbec SDK v2.7.6 and `pyorbbecsdk` are installed on the target machine.

## Run
```bash
python -m src.app_main
```

On first run, the app creates:
- `config/settings.yaml` (if missing)
- `data/database`, `data/images`, `data/calibration/history`, `data/exports`, `data/recordings`
- `logs/system.log`, `logs/camera.log`

## Developer tools
Record a short real-camera session:
```bash
python tools/record_session.py
```
Replay previously recorded FramePacket sequence:
```bash
python tools/replay_session.py data/recordings/<timestamp>/session.pkl
```

## Build (PyInstaller one-folder)
```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --name FemtoBoltGrader --add-data "config;config" --add-data "src;src" src/app_main.py
```
Output folder: `dist/FemtoBoltGrader/`

## Troubleshooting
- If camera is not detected, verify SDK install and firmware/hardware versions.
- If stream fails, stop/start grading; check `logs/camera.log`.
- If GUI fails to launch, confirm PySide6 matches Python 3.11.
