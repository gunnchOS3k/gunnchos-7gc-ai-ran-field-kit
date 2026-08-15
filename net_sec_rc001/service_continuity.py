"""Service continuity + path selection across local/LAN/Wi-Fi/Ethernet/Rel-16/NTN-sim/edge/cloud."""
from __future__ import annotations

from typing import Any


PATHS = (
    "local",
    "lan",
    "wifi",
    "ethernet",
    "cellular_rel16",
    "ntn_sim",
    "edge",
    "cloud",
)

PREFERENCE = ("ethernet", "wifi", "lan", "cellular_rel16", "edge", "cloud", "ntn_sim", "local")


def select_path(available: dict[str, bool]) -> str | None:
    for p in PREFERENCE:
        if available.get(p):
            return p
    return None


def run_service_continuity() -> dict[str, Any]:
    available = {p: True for p in PATHS}
    active = select_path(available)
    events = []
    available["ethernet"] = False
    nxt = select_path(available)
    events.append({"drop": "ethernet", "to": nxt})
    available["wifi"] = False
    available["lan"] = False
    nxt2 = select_path(available)
    events.append({"drop": "wifi+lan", "to": nxt2})
    available["cellular_rel16"] = False
    nxt3 = select_path(available)
    events.append({"drop": "cellular_rel16", "to": nxt3, "ntn_is_sim": True, "five_ga_hardware": False})
    ok = (
        active == "ethernet"
        and events[0]["to"] == "wifi"
        and events[1]["to"] == "cellular_rel16"
        and events[2]["to"] == "edge"
    )
    return {
        "schema": "gunnchos.net_sec_rc001.service_continuity.v1",
        "ok": ok,
        "paths": list(PATHS),
        "initial": active,
        "events": events,
        "RM520N_GL_NTN": False,
        "RM520N_GL_5GA": False,
        "claim_boundary": (
            "Multi-path continuity policy digital; cellular path is Rel-16 terrestrial "
            "sim; NTN path is simulation only."
        ),
        "token_candidate": "SERVICE_CONTINUITY_POLICY",
    }
