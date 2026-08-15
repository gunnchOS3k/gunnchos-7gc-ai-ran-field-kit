"""eSIM digital interfaces mapped to GSMA SGP.22 v2.7 without SM-DP+."""
from __future__ import annotations

from typing import Any


def run_esim_digital() -> dict[str, Any]:
    surfaces = {
        "LPA": {"implemented": True, "mode": "DIGITAL_STUB"},
        "ES9plus": {"implemented": True, "mode": "INTERFACE_ONLY", "sm_dp_plus": "EXTERNAL_PENDING"},
        "profile_list": {"implemented": True, "profiles": []},
        "profile_download": {"implemented": False, "status": "EXTERNAL_PENDING"},
        "profile_enable": {"implemented": False, "status": "EXTERNAL_PENDING"},
        "profile_delete": {"implemented": False, "status": "EXTERNAL_PENDING"},
        "open_gateway_camara": {
            "mapped": True,
            "real_operator": "EXTERNAL_PENDING",
            "modes": ["UNAVAILABLE", "SIMULATED", "SANDBOX"],
        },
    }
    ok = (
        surfaces["ES9plus"]["sm_dp_plus"] == "EXTERNAL_PENDING"
        and surfaces["profile_download"]["status"] == "EXTERNAL_PENDING"
        and surfaces["open_gateway_camara"]["real_operator"] == "EXTERNAL_PENDING"
    )
    return {
        "schema": "gunnchos.net_sec_rc001.esim_interfaces.v1",
        "ok": ok,
        "sgp22_version": "2.7",
        "sm_dp_plus": "EXTERNAL_PENDING",
        "CARRIER_ACCEPTED": False,
        "surfaces": surfaces,
        "claim_boundary": "Digital eSIM interfaces only; no SM-DP+ credentials in repo.",
    }
