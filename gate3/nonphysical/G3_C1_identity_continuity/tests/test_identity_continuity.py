from gate3.nonphysical.G3_C1_identity_continuity.identity_continuity import ContinuityStore

def test_enroll_and_transfer():
    s = ContinuityStore("acct-1")
    s.enroll("student_14_5", b"pk1", ["host"])
    s.enroll("handheld_hybrid", b"pk2", ["handheld"])
    out = s.transfer_session("student_14_5", "handheld_hybrid")
    assert out["ok"] is True
    assert out["token"]
