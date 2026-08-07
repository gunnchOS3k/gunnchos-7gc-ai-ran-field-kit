from gate2.nonphysical.G2_C5_signed_update.bundle.update_bundle import UpdateAdapter, UpdateBundle

def _adapter():
    return UpdateAdapter("emulator", {"update_dev": b"upd-secret"}, installed_version=1)

def test_install_ok():
    ad = _adapter()
    b = ad.sign(UpdateBundle(2, "emulator", b"payload-v2", 1, "update_dev"))
    assert ad.install(b).startswith("OK_INSTALLED")

def test_bad_sig():
    ad = _adapter()
    b = ad.sign(UpdateBundle(2, "emulator", b"x", 1, "update_dev"))
    b.signature = b"\x00" * 32
    assert ad.install(b) == "REJECT_SIGNATURE"

def test_downgrade():
    ad = _adapter()
    b = ad.sign(UpdateBundle(1, "emulator", b"old", 1, "update_dev"))
    # version == installed is not upgrade; treat as downgrade/reject when < 
    b2 = ad.sign(UpdateBundle(0, "emulator", b"older", 0, "update_dev"))
    assert ad.install(b2) == "REJECT_DOWNGRADE"

def test_rollback():
    ad = _adapter()
    b = ad.sign(UpdateBundle(3, "emulator", b"p3", 1, "update_dev"))
    ad.install(b)
    assert "OK_ROLLBACK" in ad.rollback()
