from gate3.nonphysical.G3_C4_fleet_observability.fleet_observability import FleetObservability

def test_emit_query():
    f = FleetObservability()
    f.emit("student_14_5", "heartbeat", battery=90)
    f.emit("handheld_hybrid", "alert", code="thermal_sim")
    assert len(f.query("heartbeat")) == 1
    assert f.health_summary()["event_count"] == 2
