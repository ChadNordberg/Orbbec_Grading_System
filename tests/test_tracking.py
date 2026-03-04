from src.tracking.centroid_tracker import CentroidTracker


def test_entry_zone_gate() -> None:
    t = CentroidTracker()
    tracks = t.update(0, [(2.0, 5.0, (0, 0, 4, 4))], roi_w=100)
    assert tracks[0].entered_via_entry_zone
