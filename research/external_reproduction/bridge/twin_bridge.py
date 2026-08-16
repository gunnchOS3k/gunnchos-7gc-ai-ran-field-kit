"""Bridge field-kit external reproduction ↔ gpu-nr-baseband ↔ 7gc-digital-twin.

Discovers sibling repos; never fabricates Aerial/AODT availability.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.external_reproduction.adapters.probe import probe_all
from research.external_reproduction.claim_firewall import enforce_firewall

ROOT = Path(__file__).resolve().parents[3]
REPOS = ROOT.parent


def discover() -> dict[str, Any]:
    gpu = REPOS / "gunnchos-gpu-nr-baseband-platform"
    twin = REPOS / "7gc-digital-twin"
    sionna_adapter = gpu / "tools/reference_adapters/sionna/adapter.py"
    twin_sionna_doc = twin / "industry_research_stack/NVIDIA_SIONNA_BACKEND.md"
    probe = probe_all()
    return enforce_firewall(
        {
            "schema": "gunnchos.external_reproduction.bridge.v1",
            "field_kit": str(ROOT),
            "siblings": {
                "gpu_nr_baseband": {
                    "path": str(gpu),
                    "present": gpu.is_dir(),
                    "sionna_adapter": str(sionna_adapter) if sionna_adapter.is_file() else None,
                },
                "digital_twin": {
                    "path": str(twin),
                    "present": twin.is_dir(),
                    "sionna_backend_doc": str(twin_sionna_doc) if twin_sionna_doc.is_file() else None,
                },
            },
            "adapters": probe["adapters"],
            "bridge_status": "CPU_ANALYTICAL_BRIDGE_READY",
            "aerial_bridge_status": "UNAVAILABLE_FAIL_CLOSED",
            "aodt_bridge_status": "UNAVAILABLE_FAIL_CLOSED",
            "pyaerial_bridge_status": "UNAVAILABLE_FAIL_CLOSED",
            "sionna_bridge_status": probe["adapters"]["SIONNA_PHY"]["status"],
            "IMPROVED_STATE_OF_ART": False,
            "PHYSICAL": False,
            "6G_CERTIFIED": False,
            "CARRIER_ACCEPTED": False,
        }
    )


def write_bridge(path: Path | None = None) -> dict[str, Any]:
    path = path or (ROOT / "research/external_reproduction/BRIDGE_STATUS.json")
    payload = discover()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_bridge(), indent=2))
