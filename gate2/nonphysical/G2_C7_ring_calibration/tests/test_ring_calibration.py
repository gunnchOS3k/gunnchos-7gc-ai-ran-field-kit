from gate2.nonphysical.G2_C7_ring_calibration.host_sim.ring_calibration_sim import HostRingSimulator

def test_pair_calibrate_sample():
    h = HostRingSimulator()
    assert h.pair("ring-1") == "PAIRED"
    assert h.calibrate("ring-1") == "CALIBRATED"
    out = h.sample("ring-1", now=h.rings["ring-1"].last_cal_ts)
    assert out["ok"] is True

def test_fallback_uncalibrated():
    h = HostRingSimulator()
    h.pair("ring-1")
    out = h.sample("ring-1")
    assert out["reason"] == "NOT_CALIBRATED"
    assert out["fallback"] == "host_controls"

def test_drift_fallback():
    h = HostRingSimulator()
    h.pair("ring-1")
    h.calibrate("ring-1")
    h.rings["ring-1"].drift_per_s = 1.0
    out = h.sample("ring-1", raw=(3.0, 3.0, 3.0), now=h.rings["ring-1"].last_cal_ts + 10)
    assert out["reason"] == "DRIFT_EXCEEDED"
    assert out["fallback"] == "gesture_disabled"
