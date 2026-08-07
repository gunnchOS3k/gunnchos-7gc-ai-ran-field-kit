import pytest
from gate2.nonphysical.G2_C3_battery_thermal.models.battery_thermal_model import (
    BatteryThermalModel, promote_to_measured,
)
from gate2.nonphysical.G2_C3_battery_thermal.collectors.measurement_collector import collector_status

def test_sim_labeled():
    m = BatteryThermalModel(56.0)
    s = m.simulate_step(5.0, 60.0, 100.0)
    assert s["evidence_class"] == "SIMULATED"

def test_refuse_promote():
    m = BatteryThermalModel(56.0)
    s = m.simulate_step(5.0, 60.0, 100.0)
    with pytest.raises(ValueError, match="REFUSE"):
        promote_to_measured(s)

def test_collector_pending():
    st = collector_status()
    assert st["system_token"] == "BATTERY_THERMAL_NONPHYSICAL_SYSTEM_COMPLETE"
    assert st["measurement_token"] == "REAL_MEASUREMENT_PENDING"
    assert st["samples"] == []
