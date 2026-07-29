#!/usr/bin/env python3
"""Build Oulu + NVIDIA application evidence packs (automatable portions)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import REPOS_ROOT, ROOT, git_rev, host_manifest, utc_now, write_json  # noqa: E402

OUT = ROOT / "application_evidence"


def oulu_pack() -> dict:
    repo = REPOS_ROOT / "gunnchos-emergent-service-intent-protocols"
    return {
        "pack": "oulu_genome",
        "generated_at": utc_now(),
        "one_page_summary": (
            "Resource-efficient emergent service-intent protocols for distributed "
            "edge/RAN/cloud agents under partial observability, multi-objective "
            "constraints, and TN/NTN disruption — synthetic CPU evidence only on this host."
        ),
        "research_question": (
            "Can distributed edge, RAN, and cloud agents learn compact, task-oriented "
            "signaling protocols that preserve service-continuity utility under bandwidth, "
            "energy, uncertainty, fairness, and TN/NTN disruption constraints?"
        ),
        "repository": str(repo),
        "commit": git_rev(repo),
        "paper": "paper/RESOURCE_EFFICIENT_EMERGENT_SERVICE_INTENT_PROTOCOLS.md",
        "repro_commands": ["make bootstrap", "make test", "make smoke", "make reproduce", "make paper", "make artifact"],
        "paper_status": "PREPRINT_DRAFT / PEER_REVIEW_PENDING / DOI_PENDING",
        "limitations": [
            "Results on this machine are SYNTHETIC_EXPERIMENT / CPU_MEASURED only",
            "No physical field transfer completed",
            "No independent reproduction completed",
            "No admission guarantee",
        ],
        "system_diagram": "docs/system_diagram.md",
        "host": host_manifest(),
    }


def nvidia_pack() -> dict:
    repo = REPOS_ROOT / "gunnchos-gpu-nr-baseband-platform"
    return {
        "pack": "nvidia_aerial",
        "generated_at": utc_now(),
        "architecture": "C++20 CPU reference + conditional CUDA NR baseband vertical slice, FAPI-like, fronthaul emulator, benchmark harness",
        "repository": str(repo),
        "commit": git_rev(repo),
        "paper": "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
        "code_map": ["include/nr_bb/", "src/", "cuda/", "benchmarks/", "tests/"],
        "phy_mac_coverage": ["PUSCH-oriented chain", "MIMO ZF/MMSE", "PF scheduler", "FAPI-like", "RU emulator"],
        "traceability": "3GPP-oriented notes without conformance claims",
        "benchmark_method": "Percentile latency/throughput manifests per schemas/benchmark_result.schema.json",
        "lab_readiness": "Protocols + dry-runs present; physical GPU/NIC/SDR PENDING",
        "upstream_contribution": "DOCUMENTED_IMPLEMENTATION (not upstream-accepted)",
        "exact_external_gaps": [
            "eight-plus years of work-related industry experience — NOT SATISFIED by repositories",
            "real telecom customer/partner field trials — PENDING / BLOCKED_EXTERNAL",
            "regulated commercial product ownership — NOT CLAIMED",
        ],
        "statuses": [
            "GATE4_NVIDIA_PORTABLE_PASS (if CPU tests pass)",
            "GATE4_NVIDIA_GPU_PENDING on Apple M2 host",
            "NVIDIA_TENURE_REQUIREMENT_UNSATISFIED",
            "NO_ACCEPTANCE_GUARANTEE",
        ],
        "host": host_manifest(),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    oulu = oulu_pack()
    nva = nvidia_pack()
    write_json(OUT / "OULU_APPLICATION_EVIDENCE_PACK.json", oulu)
    write_json(OUT / "NVIDIA_APPLICATION_EVIDENCE_PACK.json", nva)
    (OUT / "OULU_APPLICATION_EVIDENCE_PACK.md").write_text(
        "# Oulu GENOME Application Evidence Pack\n\n"
        + json.dumps(oulu, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "NVIDIA_APPLICATION_EVIDENCE_PACK.md").write_text(
        "# NVIDIA Aerial Application Evidence Pack\n\n"
        + json.dumps(nva, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "oulu": str(OUT / "OULU_APPLICATION_EVIDENCE_PACK.json"), "nvidia": str(OUT / "NVIDIA_APPLICATION_EVIDENCE_PACK.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
