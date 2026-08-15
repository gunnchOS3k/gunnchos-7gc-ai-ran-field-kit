"""Service continuity + path selection across local/LAN/Wi-Fi/Ethernet/5G/NTN-sim/edge/cloud."""
from __future__ import annotations

from typing import Any


PATHS = (
    "local",
    "lan",
    "wifi",
    "ethernet",
    "cellular_5ga",
    "ntn_sim",
    "edge",
    "cloud",
)

PREFERENCE = ("ethernet", "wifi", "lan", "cellular_5ga", "edge", "cloud", "ntn_sim", "local")


def select_path(available: dict[str, bool]) -> str | None:
    for p in PREFERENCE:
        if available.get(p):
            return p
    return None


def run_service_continuity() -> dict[str, Any]:
    available = {p: True for p in PATHS}
    active = select_path(available)
    events = []
    # Drop ethernet → wifi
    available["ethernet"] = False
    nxt = select_path(available)
    events.append({"drop": "ethernet", "to": nxt})
    # Drop wifi → cellular
    available["wifi"] = False
    available["lan"] = False
    nxt2 = select_path(available)
    events.append({"drop": "wifi+lan", "to": nxt2})
    # Cellular loss → ntn_sim (simulated only)
    available["cellular_5ga"] = False
    nxt3 = select_path(available)
    events.append({"drop": "cellular_5ga", "to": nxt3, "ntn_is_sim": True})
    ok = active == "ethernet" and events[0]["to"] == "wifi" and events[1]["to"] == "cellular_5ga" and events[2]["to"] == "edge"
    # edge preferred over cloud/ntn_sim/local per PREFERENCE after cellular drop... 
    # Wait: preference after cellular_5ga is edge, cloud, ntn_sim, local — edge still True → edge. Good.
    return {
        "schema": "gunnchos.net_sec_rc001.service_continuity.v1",
        "ok": ok,
        "paths": list(PATHS),
        "initial": active,
        "events": events,
        "RM520N_GL_NTN": False,
        "claim_boundary": "Multi-path continuity policy digital; NTN path is simulation.",
        "token_candidate": "SERVICE_CONTINUITY_POLICY",
    }
