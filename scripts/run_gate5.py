#!/usr/bin/env python3
"""Gate 5 orchestrator — publication, artifact, release-candidate readiness."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import (  # noqa: E402
    REPOS_ROOT,
    ROOT,
    host_manifest,
    run_cmd,
    update_master_status,
    utc_now,
    verify_lock,
    write_json,
)

OULU = REPOS_ROOT / "gunnchos-emergent-service-intent-protocols"
NVA = REPOS_ROOT / "gunnchos-gpu-nr-baseband-platform"
OUT = ROOT / "orchestration" / "gates_4_6" / "gate5"


def check_paper(repo: Path, rel: str) -> dict:
    path = repo / rel
    return {
        "path": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
    }


def run_repo_gate5(repo: Path, name: str) -> dict:
    if not repo.is_dir():
        return {"ok": False, "error": f"{name} missing"}
    paper = run_cmd(["make", "paper"], cwd=repo)
    artifact = run_cmd(["make", "artifact"], cwd=repo)
    reproduce = run_cmd(["make", "reproduce"], cwd=repo)
    ok = paper["ok"] and artifact["ok"] and reproduce["ok"]
    return {
        "ok": ok,
        "paper": paper,
        "artifact": artifact,
        "reproduce": reproduce,
        "status": "RELEASE_CANDIDATE_READY" if ok else "GATE5_FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-lock", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    lock = verify_lock(fail_on_mismatch=not args.skip_lock) if not args.skip_lock else {"ok": True, "skipped": True}

    oulu = run_repo_gate5(OULU, "oulu")
    nva = run_repo_gate5(NVA, "nvidia")
    papers = {
        "oulu_md": check_paper(OULU, "paper/RESOURCE_EFFICIENT_EMERGENT_SERVICE_INTENT_PROTOCOLS.md"),
        "nvidia_md": check_paper(NVA, "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md"),
    }

    ok = oulu.get("ok") and nva.get("ok") and papers["oulu_md"]["exists"] and papers["nvidia_md"]["exists"]
    statuses = {
        "GATE5_RELEASE_CANDIDATE": "GATE5_RELEASE_CANDIDATE_PASS" if ok else "GATE5_RELEASE_CANDIDATE_FAIL",
        "GATE5_DOI": "DOI_PENDING",
        "GATE5_INDEPENDENT_REPRODUCTION": "INDEPENDENT_REPRODUCTION_PENDING",
        "GATE5_PEER_REVIEW": "PEER_REVIEW_PENDING",
        "ACCEPTANCE": "NO_ACCEPTANCE_GUARANTEE",
    }
    report = {
        "gate": "5",
        "started": utc_now(),
        "host": host_manifest(),
        "lock": lock,
        "oulu": oulu,
        "nvidia": nva,
        "papers": papers,
        "statuses": statuses,
        "finished": utc_now(),
    }
    write_json(OUT / "gate5_report.json", report)
    update_master_status(statuses, notes=[f"report={OUT / 'gate5_report.json'}"])
    print(json.dumps({"ok": ok, "statuses": statuses}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
