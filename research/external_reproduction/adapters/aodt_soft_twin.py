"""Soft AODT twin adapter — discovery / wiring only.

Never returns fabricated AODT coverage / ABS placement numbers.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research.external_reproduction.adapters.probe import probe_one
from research.external_reproduction.claim_firewall import enforce_firewall
from research.external_reproduction.bridge.twin_bridge import discover

ROOT = Path(__file__).resolve().parents[3]


def soft_twin_status() -> dict[str, Any]:
    aodt = probe_one("AODT", "aodt")
    bridge = discover()
    twin = bridge["siblings"]["digital_twin"]
    return enforce_firewall(
        {
            "schema": "gunnchos.aodt_soft_twin.v1",
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": "SOFT_ADAPTER_DISCOVERY_ONLY",
            "aodt_import": aodt.to_dict(),
            "digital_twin_repo": twin,
            "executable": False if not aodt.present else True,
            "status": aodt.status,
            "note": (
                "Soft twin documents sibling digital-twin + gpu-nr bridges; "
                "does not emit fake AODT KPIs when import fails."
            ),
            "AODT_VALIDATED": False,
            "IMPROVED_STATE_OF_ART": False,
            "PHYSICAL": False,
            "OTA": False,
        }
    )


def write_status(path: Path | None = None) -> dict[str, Any]:
    path = path or (
        ROOT / "artifacts/external_reproduction/C_PKT_003/NVIDIA/AODT_SOFT_TWIN.json"
    )
    payload = soft_twin_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
