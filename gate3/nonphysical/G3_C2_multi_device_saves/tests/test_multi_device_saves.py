import pytest
from gate3.nonphysical.G3_C2_multi_device_saves.multi_device_saves import SaveStore

def test_cross_device_save():
    s = SaveStore()
    s.put("a1", "beatlink-party", "student_14_5", {"score": 10})
    slot = s.put("a1", "beatlink-party", "handheld_hybrid", {"score": 12})
    assert slot.rev == 2
    assert s.get("a1", "beatlink-party").payload["score"] == 12

def test_stale_conflict():
    s = SaveStore()
    s.put("a1", "x", "d1", {"v": 1})
    with pytest.raises(ValueError, match="CONFLICT"):
        s.put("a1", "x", "d2", {"v": 0}, rev=0)
