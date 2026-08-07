from gate2.nonphysical.G2_C2_display_controls.hal.display_controls_hal import (
    DisplayControlsHAL, EmulatorDisplay, MockControls, PhysicalCollectorStub,
)

def test_emulator_mock_labeled_nonphysical():
    hal = DisplayControlsHAL(EmulatorDisplay(), MockControls())
    hal.render(b"\x00" * 16)
    assert "NONPHYSICAL" in hal.claim_label()
    assert hal.display.frames == 1

def test_physical_collector_does_not_fabricate():
    stub = PhysicalCollectorStub()
    out = stub.collect()
    assert out["evidence_class"] == "PHYSICAL_PENDING"
    assert out["samples"] == []
