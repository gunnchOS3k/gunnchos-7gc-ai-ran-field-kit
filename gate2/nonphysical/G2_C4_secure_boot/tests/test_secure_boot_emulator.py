import pytest
from gate2.nonphysical.G2_C4_secure_boot.emulator.secure_boot_emulator import SecureBootEmulator

def test_sign_verify_ok():
    emu = SecureBootEmulator({"boot_dev": b"dev-secret"})
    img = emu.sign("bl2", b"payload", "boot_dev", 1)
    assert emu.verify(img) is True

def test_bad_signature():
    emu = SecureBootEmulator({"boot_dev": b"dev-secret"})
    img = emu.sign("bl2", b"payload", "boot_dev", 1)
    img.signature = b"\x00" * 32
    assert emu.verify(img) is False

def test_rollback_rejected():
    emu = SecureBootEmulator({"boot_dev": b"dev-secret"})
    assert emu.verify(emu.sign("kernel", b"k", "boot_dev", 2))
    assert emu.verify(emu.sign("kernel", b"k-old", "boot_dev", 1)) is False

def test_unknown_key():
    emu = SecureBootEmulator({"boot_dev": b"dev-secret"})
    img = emu.sign("bl2", b"x", "boot_dev", 1)
    img.key_id = "prod_unknown"
    assert emu.verify(img) is False
