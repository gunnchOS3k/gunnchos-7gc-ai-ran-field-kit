#!/usr/bin/env python3
"""Gate 4 orchestrator — Oulu research + NVIDIA baseband automatable tracks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import (  # noqa: E402
    REPOS_ROOT,
    ROOT,
    detect_cuda,
    host_manifest,
    run_cmd,
    update_master_status,
    utc_now,
    verify_lock,
    write_json,
)

OULU = REPOS_ROOT / "gunnchos-emergent-service-intent-protocols"
NVA = REPOS_ROOT / "gunnchos-gpu-nr-baseband-platform"
OUT = ROOT / "orchestration" / "gates_4_6" / "gate4"


def run_oulu(mode: str = "smoke") -> dict:
    if not OULU.is_dir():
        return {"ok": False, "error": "Oulu repo missing", "status": "FAIL"}
    makefile = OULU / "Makefile"
    if not makefile.exists():
        return {"ok": False, "error": "Makefile missing", "status": "FAIL"}
    target = "smoke" if mode == "smoke" else "test"
    bootstrap = run_cmd(["make", "bootstrap"], cwd=OULU)
    test = run_cmd(["make", target], cwd=OULU)
    ok = bootstrap["ok"] and test["ok"]
    return {
        "ok": ok,
        "status": "GATE4_OULU_AUTOMATED_PASS" if ok else "GATE4_OULU_FAIL",
        "bootstrap": bootstrap,
        "test": test,
        "evidence_label": "SYNTHETIC_EXPERIMENT" if ok else "FAILED",
    }


def run_nvidia_cpu() -> dict:
    if not NVA.is_dir():
        return {"ok": False, "error": "NVIDIA baseband repo missing", "status": "FAIL"}
    if not (NVA / "Makefile").exists():
        return {"ok": False, "error": "Makefile missing", "status": "FAIL"}
    bootstrap = run_cmd(["make", "bootstrap"], cwd=NVA)
    test = run_cmd(["make", "test"], cwd=NVA)
    smoke = run_cmd(["make", "smoke"], cwd=NVA)
    ok = bootstrap["ok"] and test["ok"] and smoke["ok"]
    return {
        "ok": ok,
        "status": "GATE4_NVIDIA_PORTABLE_PASS" if ok else "GATE4_NVIDIA_PORTABLE_FAIL",
        "bootstrap": bootstrap,
        "test": test,
        "smoke": smoke,
        "evidence_label": "CPU_MEASURED" if ok else "FAILED",
    }


def run_nvidia_gpu() -> dict:
    cuda = detect_cuda()
    if cuda["status"] == "BLOCKED_HARDWARE":
        blocked = {
            "ok": True,
            "status": "GATE4_NVIDIA_GPU_PENDING",
            "evidence_label": "BLOCKED_HARDWARE",
            "cuda": cuda,
            "note": "No NVIDIA GPU/CUDA on this host. Harness must exist; results not fabricated.",
        }
        # Still invoke make gate4-gpu if present to ensure honest failure/pending path
        if (NVA / "Makefile").exists():
            blocked["make_gate4_gpu"] = run_cmd(["make", "gate4-gpu"], cwd=NVA)
        return blocked
    test = run_cmd(["make", "gate4-gpu"], cwd=NVA)
    return {
        "ok": test["ok"],
        "status": "GATE4_NVIDIA_GPU_PASS" if test["ok"] else "GATE4_NVIDIA_GPU_FAIL",
        "evidence_label": "GPU_MEASURED" if test["ok"] else "FAILED",
        "cuda": cuda,
        "test": test,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", choices=["all", "oulu", "nvidia-cpu", "nvidia-gpu"], default="all")
    parser.add_argument("--skip-lock", action="store_true")
    parser.add_argument("--update-lock-commits", action="store_true", help="Rewrite lock commits from checkout (maintenance)")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    lock_report = verify_lock(fail_on_mismatch=not args.skip_lock) if not args.skip_lock else {"ok": True, "skipped": True}

    report: dict = {
        "gate": "4",
        "program": "oulu_genome_nvidia_aerial",
        "started": utc_now(),
        "host": host_manifest(),
        "lock": lock_report,
        "tracks": {},
    }

    if args.track in ("all", "oulu"):
        report["tracks"]["oulu"] = run_oulu()
    if args.track in ("all", "nvidia-cpu"):
        report["tracks"]["nvidia_cpu"] = run_nvidia_cpu()
    if args.track in ("all", "nvidia-gpu"):
        report["tracks"]["nvidia_gpu"] = run_nvidia_gpu()

    statuses = {
        "GATE4_OULU": report["tracks"].get("oulu", {}).get("status", "SKIPPED"),
        "GATE4_NVIDIA_PORTABLE": report["tracks"].get("nvidia_cpu", {}).get("status", "SKIPPED"),
        "GATE4_NVIDIA_GPU": report["tracks"].get("nvidia_gpu", {}).get("status", "SKIPPED"),
        "PHYSICAL_EVIDENCE": "PHYSICAL_EVIDENCE_PENDING",
        "EXTERNAL_VALIDATION": "EXTERNAL_VALIDATION_PENDING",
        "NVIDIA_TENURE": "NVIDIA_TENURE_REQUIREMENT_UNSATISFIED",
        "ACCEPTANCE": "NO_ACCEPTANCE_GUARANTEE",
    }
    report["statuses"] = statuses
    report["finished"] = utc_now()
    write_json(OUT / "gate4_report.json", report)
    update_master_status(statuses, notes=[f"Gate4 track={args.track}", f"report={OUT / 'gate4_report.json'}"])

    fails = [
        t
        for name, t in report["tracks"].items()
        if name != "nvidia_gpu" and not t.get("ok", False)
    ]
    # GPU pending is success-of-honesty
    gpu = report["tracks"].get("nvidia_gpu")
    if gpu and gpu.get("status") not in (
        "GATE4_NVIDIA_GPU_PASS",
        "GATE4_NVIDIA_GPU_PENDING",
    ):
        fails.append(gpu)

    print(json.dumps({"ok": not fails, "statuses": statuses, "report": str(OUT / "gate4_report.json")}, indent=2))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
