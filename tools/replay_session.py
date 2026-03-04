from __future__ import annotations

import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/replay_session.py <data/recordings/.../session.pkl>")
        return 1

    p = Path(sys.argv[1])
    with p.open("rb") as fh:
        frames = pickle.load(fh)
    for packet in frames:
        print(packet.frame_index, packet.depth_timestamp_ns, packet.rgb_timestamp_ns)
    print(f"Replayed {len(frames)} FramePacket objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
