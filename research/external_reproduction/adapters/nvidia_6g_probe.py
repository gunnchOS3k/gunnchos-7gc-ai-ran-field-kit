"""nvidia-6g-probe — FAIL CLOSED on Mac / no-CUDA hosts.

Never fabricates AODT / pyAerial / Aerial / Sionna availability.
"""
from __future__ import annotations

import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research.external_reproduction.adapters.probe import probe_all
from research.external_reproduction.claim_firewall import enforce_firewall

ROOT = Path(__file__).resolve().parents[3]


def _nvidia_smi() -> dict[str, Any]:
    path = shutil.which("nvidia-smi")
    if not path:
        return {"present": False, "status": "UNAVAILABLE_FAIL_CLOSED", "path": None}
    return {"present": True, "status": "PRESENT", "path": path}


def probe_host() -> dict[str, Any]:
    system = platform.system()
    machine = platform.machine()
    smi = _nvidia_smi()
    adapters = probe_all()
    is_mac = system == "Darwin"
    cudaish = smi["present"] and any(
        adapters["adapters"][k]["present"]
        for k in ("SIONNA_PHY", "AODT", "PYAERIAL", "AERIAL_SDK")
    )

    if is_mac:
        status = "FAIL_CLOSED_MAC"
        rationale = [
            "Host is macOS — NVIDIA Aerial / CUDA RAN / AODT / pyAerial are not claimable here",
            "CPU+NumPy analytical path remains allowed when declared explicitly",
            "Use Linux NVIDIA runner packet for GPU path",
        ]
    elif not smi["present"]:
        status = "FAIL_CLOSED_NO_NVIDIA_SMI"
        rationale = ["nvidia-smi missing", "No silent fake GPU backends"]
    elif not cudaish:
        status = "FAIL_CLOSED_NO_AERIAL_STACK"
        rationale = ["nvidia-smi present but Sionna/AODT/pyAerial/Aerial not importable"]
    else:
        status = "GPU_STACK_DETECTABLE"
        rationale = ["At least one NVIDIA/Sionna backend importable — still no OTA/cert claim"]

    payload = enforce_firewall(
        {
            "schema": "gunnchos.nvidia_6g_probe.v1",
            "probe_id": "nvidia-6g-probe",
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host": {
                "system": system,
                "machine": machine,
                "python": sys.version.split()[0],
                "platform": platform.platform(),
            },
            "status": status,
            "status_rationale": rationale,
            "nvidia_smi": smi,
            "adapters": adapters["adapters"],
            "linux_runner_packet": "artifacts/external_reproduction/C_PKT_003/NVIDIA/LINUX_NVIDIA_RUNNER_PACKET.md",
            "fake_forbidden": {
                "AODT": True,
                "pyAerial": True,
                "Aerial": True,
                "Sionna_silent_stub": True,
                "OTA": True,
            },
            "NVIDIA_AERIAL_VALIDATED": False,
            "AODT_VALIDATED": False,
            "PYAERIAL_VALIDATED": False,
            "IMPROVED_STATE_OF_ART": False,
            "PHYSICAL": False,
            "OTA": False,
        }
    )
    return payload


def write_probe(path: Path | None = None) -> dict[str, Any]:
    path = path or (
        ROOT / "artifacts/external_reproduction/C_PKT_003/NVIDIA/NVIDIA_6G_PROBE.json"
    )
    payload = probe_host()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # mirror under research
    mirror = ROOT / "research/external_reproduction/NVIDIA_6G_PROBE.json"
    mirror.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    payload = write_probe()
    print(json.dumps(payload, indent=2, sort_keys=True))
    # Non-zero on Mac / fail-closed so CI can gate GPU claims
    if payload["status"].startswith("FAIL_CLOSED"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
