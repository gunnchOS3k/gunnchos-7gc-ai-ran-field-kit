"""Battery/thermal models — MODELED/SIMULATED only."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class BatteryThermalModel:
    capacity_wh: float
    thermal_r_c_per_w: float = 4.0
    ambient_c: float = 25.0

    def simulate_step(self, load_w: float, dt_s: float, soc: float) -> dict:
        # Simple coulomb + thermal RC — labeled SIMULATED
        energy = self.capacity_wh * (soc / 100.0)
        energy = max(0.0, energy - load_w * dt_s / 3600.0)
        soc_out = 100.0 * energy / self.capacity_wh if self.capacity_wh else 0.0
        temp = self.ambient_c + load_w * self.thermal_r_c_per_w
        return {
            "evidence_class": "SIMULATED",
            "battery_soc_pct": round(soc_out, 3),
            "battery_voltage_v": round(3.3 + 0.9 * (soc_out / 100.0), 3),
            "skin_temp_c": round(temp, 3),
            "soc_temp_c": round(temp + 2.0, 3),
            "source": "battery_thermal_model",
        }

def promote_to_measured(sample: dict) -> dict:
    """Hard-fail promotion path — sim must never become measured."""
    if sample.get("evidence_class") in ("SIMULATED", "MODELED"):
        raise ValueError("REFUSE: cannot promote SIMULATED/MODELED to MEASURED")
    return sample
