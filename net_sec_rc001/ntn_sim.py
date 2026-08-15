"""NTN abstraction/simulation — LEO/MEO/GEO. Does NOT claim RM520N NTN."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ORBITS = ("LEO", "MEO", "GEO")


@dataclass
class NtnOrbitModel:
    orbit: str
    one_way_delay_ms: float
    max_doppler_hz: float
    visibility_fraction: float
    handover_interval_s: float
    gap_probability: float

    def sample(self) -> dict[str, Any]:
        return {
            "orbit": self.orbit,
            "one_way_delay_ms": self.one_way_delay_ms,
            "round_trip_delay_ms": round(self.one_way_delay_ms * 2, 2),
            "max_doppler_hz": self.max_doppler_hz,
            "visibility_fraction": self.visibility_fraction,
            "handover_interval_s": self.handover_interval_s,
            "service_gap_probability": self.gap_probability,
            "rm520n_ntn_claimed": False,
        }


DEFAULT_MODELS = {
    "LEO": NtnOrbitModel("LEO", 25.0, 40000.0, 0.72, 480.0, 0.08),
    "MEO": NtnOrbitModel("MEO", 90.0, 8000.0, 0.85, 1800.0, 0.04),
    "GEO": NtnOrbitModel("GEO", 270.0, 50.0, 0.98, 86400.0, 0.01),
}


def run_ntn_simulation() -> dict[str, Any]:
    samples = {k: m.sample() for k, m in DEFAULT_MODELS.items()}
    handover = {
        "from": "LEO-A",
        "to": "LEO-B",
        "break_before_make": True,
        "gap_ms": 120.0,
        "policy": "simulate_gap_then_resume",
    }
    ok = all(o in samples for o in ORBITS) and samples["LEO"]["rm520n_ntn_claimed"] is False
    return {
        "schema": "gunnchos.net_sec_rc001.ntn_sim.v1",
        "ok": ok,
        "orbits": samples,
        "handover": handover,
        "visibility_gaps_modeled": True,
        "doppler_modeled": True,
        "RM520N_GL_NTN": False,
        "REAL_NTN_MODEM_VALIDATED": False,
        "claim_boundary": "Software NTN simulation only; RM520N-GL is not NTN.",
        "token_candidate": "NTN_SIMULATION_RUNTIME",
    }
