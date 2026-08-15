"""5G-Advanced terrestrial digital runtime for Quectel RM520N-GL.

Rel-16 NSA+SA Sub-6 only. NOT NTN/6G capable. CARRIER EXTERNAL_PENDING.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CLAIM = (
    "Simulated Quectel RM520N-GL Rel-16 NSA+SA Sub-6 terrestrial path. "
    "Not NTN. Not 6G. CARRIER_ACCEPTED=false. CARRIER EXTERNAL_PENDING."
)


@dataclass
class RM520NTerrestrialDigital:
    sku: str = "RM520N-GL"
    release: str = "Rel-16"
    modes: tuple[str, ...] = ("NSA", "SA")
    band_class: str = "Sub-6"
    ntn_capable: bool = False
    six_g_capable: bool = False
    carrier_status: str = "EXTERNAL_PENDING"
    state: dict[str, Any] = field(default_factory=dict)

    def discovery(self) -> dict[str, Any]:
        self.state["discovered"] = True
        return {"ok": True, "sku": self.sku, "transports": ["mbim", "qmi", "modemmanager"], "ntn": False}

    def sim(self, present: bool = True) -> dict[str, Any]:
        self.state["sim_present"] = present
        self.state["sim_ready"] = present
        return {"ok": present, "present": present, "ready": present, "pin_required": False}

    def esim_interface(self) -> dict[str, Any]:
        return {
            "ok": True,
            "interface": "LPA_DIGITAL",
            "sgp22_mapped": "2.7",
            "sm_dp_plus": "EXTERNAL_PENDING",
            "profile_download": "EXTERNAL_PENDING",
            "CARRIER": "EXTERNAL_PENDING",
        }

    def register(self, mode: str = "SA") -> dict[str, Any]:
        if mode not in self.modes:
            return {"ok": False, "reason": "unsupported_mode"}
        if not self.state.get("sim_ready"):
            return {"ok": False, "reason": "sim_not_ready"}
        self.state["registered"] = True
        self.state["mode"] = mode
        tech = "nr5g-sa" if mode == "SA" else "nr5g-nsa"
        return {"ok": True, "mode": mode, "plmn": "00101", "tech": tech}

    def signal(self) -> dict[str, Any]:
        return {"rsrp_dbm": -88.0, "rsrq_db": -10.0, "sinr_db": 12.0, "band": "n78", "ntn": False}

    def bearer(self, apn: str = "internet") -> dict[str, Any]:
        if not self.state.get("registered"):
            return {"ok": False, "reason": "not_registered"}
        self.state["bearer"] = True
        self.state["apn"] = apn
        return {"ok": True, "apn": apn, "pdn": "ipv4v6", "qos": "default"}

    def connect(self) -> dict[str, Any]:
        if not self.state.get("bearer"):
            return {"ok": False, "reason": "no_bearer"}
        self.state["connected"] = True
        return {"ok": True, "connected": True, "path": "terrestrial_5ga"}

    def failover(self, to: str = "wifi") -> dict[str, Any]:
        self.state["active_path"] = to
        return {"ok": True, "from": "cellular", "to": to, "policy": "service_continuity"}

    def telemetry(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "registered": bool(self.state.get("registered")),
            "connected": bool(self.state.get("connected")),
            "signal": self.signal(),
            "apn": self.state.get("apn"),
            "mode": self.state.get("mode"),
            "ntn_claimed": False,
            "six_g_claimed": False,
        }

    def data_policy(self) -> dict[str, Any]:
        return {
            "apn_allowlist": ["internet", "campus.internet"],
            "metered": True,
            "roaming_default": "deny_until_confirmed",
            "CARRIER": "EXTERNAL_PENDING",
        }

    def run(self) -> dict[str, Any]:
        self.state.clear()
        seq = [
            ("discovery", self.discovery()),
            ("sim", self.sim()),
            ("esim_interface", self.esim_interface()),
            ("register_sa", self.register("SA")),
            ("signal", self.signal()),
            ("bearer", self.bearer("internet")),
            ("connect", self.connect()),
            ("failover", self.failover("wifi")),
            ("telemetry", self.telemetry()),
            ("data_policy", self.data_policy()),
        ]
        nsa = RM520NTerrestrialDigital()
        nsa.sim(True)
        nsa_reg = nsa.register("NSA")
        ok = all(
            [
                seq[0][1]["ok"],
                seq[1][1]["ok"],
                seq[2][1]["sm_dp_plus"] == "EXTERNAL_PENDING",
                seq[3][1]["ok"],
                seq[5][1]["ok"],
                seq[6][1]["ok"],
                seq[7][1]["ok"],
                nsa_reg["ok"],
                self.ntn_capable is False,
                self.six_g_capable is False,
                self.carrier_status == "EXTERNAL_PENDING",
            ]
        )
        return {
            "schema": "gunnchos.net_sec_rc001.terrestrial_5ga.v1",
            "ok": ok,
            "sku": self.sku,
            "release": self.release,
            "modes_exercised": ["SA", "NSA"],
            "band_class": self.band_class,
            "ntn_capable": False,
            "six_g_capable": False,
            "CARRIER": "EXTERNAL_PENDING",
            "CARRIER_ACCEPTED": False,
            "STANDARDIZED_6G": False,
            "steps": [{"op": k, "result": v} for k, v in seq],
            "nsa_register": nsa_reg,
            "claim_boundary": CLAIM,
            "token_candidate": "5GA_TERRESTRIAL_DIGITAL_RUNTIME",
        }
