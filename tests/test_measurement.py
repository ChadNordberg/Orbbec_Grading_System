from src.measure.measurement import trimmed_mean


def test_trimmed_mean_basic() -> None:
    assert trimmed_mean([1, 2, 3, 4, 100], 1) == 3.0
