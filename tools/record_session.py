from __future__ import annotations

import pickle
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.camera.femto_client import FemtoBoltClient


def main() -> int:
    out_dir = ROOT / "data/recordings" / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    client = FemtoBoltClient()
    status = client.connect()
    if not status.connected:
        print(f"Camera connect failed: {status.detail}")
        return 1

    frames = []
    for _ in range(90):
        packet = client.get_frame()
        if packet:
            frames.append(packet)
    client.disconnect()

    with (out_dir / "session.pkl").open("wb") as fh:
        pickle.dump(frames, fh)
    print(f"Recorded {len(frames)} frames to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
