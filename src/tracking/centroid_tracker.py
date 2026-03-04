from __future__ import annotations

from dataclasses import dataclass, field

from src.utils.contracts import Track


@dataclass(slots=True)
class TrackerConfig:
    confirm_frames: int = 3
    exit_confirm_frames: int = 5
    coast_frames: int = 10
    entry_zone_fraction: float = 0.05
    gate_px: float = 60.0


@dataclass(slots=True)
class CentroidTracker:
    cfg: TrackerConfig = field(default_factory=TrackerConfig)
    _next_id: int = 1
    tracks: dict[int, Track] = field(default_factory=dict)

    def update(self, frame_index: int, detections: list[tuple[float, float, tuple[int, int, int, int]]], roi_w: int) -> list[Track]:
        updated: list[Track] = []
        for cx, cy, bbox in detections:
            chosen = None
            best = float("inf")
            for t in self.tracks.values():
                if not t.mask_centroid_history:
                    continue
                px, py = t.mask_centroid_history[-1]
                d = abs(px - cx) + abs(py - cy)
                if d < best and d <= self.cfg.gate_px:
                    chosen = t
                    best = d
            if chosen is None:
                t = Track(unique_id=self._next_id, state="candidate")
                self._next_id += 1
                t.entered_via_entry_zone = cx <= roi_w * self.cfg.entry_zone_fraction
                self.tracks[t.unique_id] = t
                chosen = t
            chosen.mask_centroid_history.append((cx, cy))
            chosen.bbox_history.append(bbox)
            chosen.last_seen_frame = frame_index
            chosen.missing_count = 0
            if len(chosen.mask_centroid_history) >= self.cfg.confirm_frames and chosen.entered_via_entry_zone:
                chosen.state = "confirmed"
            updated.append(chosen)

        for t in self.tracks.values():
            if t.last_seen_frame != frame_index:
                t.missing_count += 1
                if t.missing_count > self.cfg.coast_frames:
                    t.state = "dropped"
        return updated
