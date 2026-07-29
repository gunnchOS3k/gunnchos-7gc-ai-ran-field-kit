#!/usr/bin/env python3
"""Build portable Oulu + NVIDIA application evidence packs (no absolute local paths)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import REPOS_ROOT, ROOT, git_branch, git_rev, utc_now, write_json  # noqa: E402
from run_corrective_validators import validate_application_pack  # noqa: E402

OUT = ROOT / "application_evidence"

OULU_URL = "https://github.com/gunnchOS3k/gunnchos-emergent-service-intent-protocols"
NVIDIA_URL = "https://github.com/gunnchOS3k/gunnchos-gpu-nr-baseband-platform"


def _require_commit(repo: Path, name: str) -> str:
    commit = git_rev(repo)
    if not commit:
        raise SystemExit(f"application pack blocked: commit is null for {name} at {repo}")
    return commit


def oulu_pack() -> dict:
    repo = REPOS_ROOT / "gunnchos-emergent-service-intent-protocols"
    commit = _require_commit(repo, "oulu")
    return {
        "pack": "oulu_genome",
        "generated_at": utc_now(),
        "owner_name": "gunnchOS3k/gunnchos-emergent-service-intent-protocols",
        "repository_url": OULU_URL,
        "canonical_repository_url": OULU_URL,
        "branch": git_branch(repo) or "cursor/corrective-depth-gates-4-6",
        "commit": commit,
        "release_candidate_tag": None,
        "visibility": "private",
        "reviewer_access": "REVIEWER_ACCESS_BLOCKED_USER_APPROVAL",
        "publication_status": "BLOCKED_USER_APPROVAL",
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
        "paper": "paper/RESOURCE_EFFICIENT_EMERGENT_SERVICE_INTENT_PROTOCOLS.md",
        "manuscript_artifact": "paper/RESOURCE_EFFICIENT_EMERGENT_SERVICE_INTENT_PROTOCOLS.md",
        "reproduction_command": "make bootstrap && make test && make smoke && make causal-tests && make paper && make artifact",
        "repro_commands": [
            "make bootstrap",
            "make test",
            "make smoke",
            "make causal-tests",
            "make paper",
            "make artifact",
            "make reproduce-clean",
        ],
        "evidence_class": "SYNTHETIC_EXPERIMENT",
        "evidence_status": "GATE4_OULU_FUNCTIONAL_SCAFFOLD_PASS",
        "scientific_status": "GATE4_OULU_SCIENTIFIC_EVIDENCE_PENDING",
        "paper_status": "GATE5_DRAFT_PACKAGE_PASS / GATE5_PUBLICATION_RELEASE_PENDING / GATE5_DOI_PENDING / GATE5_PEER_REVIEW_PENDING",
        "selected_results": [],
        "limitations": [
            "Results on this machine are SYNTHETIC_EXPERIMENT / CPU_MEASURED only",
            "No physical field transfer completed",
            "No independent reproduction completed",
            "No Oulu admission guarantee",
            "Author reproduction is not independent reproduction",
        ],
        "physical_blockers": ["54-cell physical pilot", "real user study"],
        "external_blockers": ["independent reproduction", "peer review", "DOI"],
        "system_diagram": "docs/system_diagram.md",
        "host_class": "author_laptop_cpu_only",
        "non_claims": ["NO_ACCEPTANCE_GUARANTEE"],
    }


def nvidia_pack() -> dict:
    repo = REPOS_ROOT / "gunnchos-gpu-nr-baseband-platform"
    commit = _require_commit(repo, "nvidia")
    return {
        "pack": "nvidia_aerial",
        "generated_at": utc_now(),
        "owner_name": "gunnchOS3k/gunnchos-gpu-nr-baseband-platform",
        "repository_url": NVIDIA_URL,
        "canonical_repository_url": NVIDIA_URL,
        "branch": git_branch(repo) or "cursor/corrective-depth-gates-4-6",
        "commit": commit,
        "release_candidate_tag": None,
        "visibility": "private",
        "reviewer_access": "REVIEWER_ACCESS_BLOCKED_USER_APPROVAL",
        "publication_status": "BLOCKED_USER_APPROVAL",
        "architecture": (
            "C++20 CPU reference + conditional CUDA NR baseband path; educational modules "
            "separated; FAPI-like / fronthaul emulator; benchmark harness"
        ),
        "paper": "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
        "manuscript_artifact": "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
        "reproduction_command": "make bootstrap && make test && make gate4-cpu-reference && make gate6-dry-run && make paper",
        "code_map": ["include/nr_bb/", "src/", "educational/", "cuda/", "benchmarks/", "tests/"],
        "phy_mac_coverage": ["PUSCH-oriented chain", "MIMO ZF/MMSE", "scheduler path", "FAPI-like", "RU emulator"],
        "traceability": "3GPP-oriented notes without conformance claims",
        "benchmark_method": "Percentile latency/throughput manifests; GPU numeric results forbidden without NVIDIA hardware",
        "lab_readiness": "Protocols + dry-runs present; physical GPU/NIC/SDR PENDING",
        "upstream_contribution": "DOCUMENTED_IMPLEMENTATION (not upstream-accepted)",
        "evidence_class": "CPU_MEASURED / BLOCKED_HARDWARE (GPU)",
        "evidence_status": "GATE4_NVIDIA_EDUCATIONAL_CPU_PASS",
        "aerial_status": "GATE4_NVIDIA_AERIAL_DEPTH_PENDING",
        "exact_external_gaps": [
            "eight-plus years of work-related industry experience — NOT SATISFIED by repositories",
            "real telecom customer/partner field trials — PENDING / BLOCKED_EXTERNAL",
            "regulated commercial product ownership — NOT CLAIMED",
        ],
        "statuses": [
            "GATE4_NVIDIA_EDUCATIONAL_CPU_PASS",
            "GATE4_NVIDIA_AERIAL_DEPTH_PENDING",
            "GATE4_NVIDIA_GPU_PENDING",
            "NVIDIA_TENURE_REQUIREMENT_UNSATISFIED",
            "NVIDIA_CUSTOMER_TRIAL_REQUIREMENT_PENDING",
            "NO_ACCEPTANCE_GUARANTEE",
        ],
        "physical_blockers": ["NVIDIA GPU measurements", "Nsight", "NIC/PTP", "SDR/RU"],
        "external_blockers": ["tenure gap", "customer trial", "upstream acceptance"],
        "host_class": "author_laptop_cpu_only",
        "non_claims": [
            "NO_ACCEPTANCE_GUARANTEE",
            "no NVIDIA Aerial equivalence",
            "no 3GPP certification",
            "no carrier-grade claim",
        ],
    }


def _assert_portable(pack_dir: Path) -> None:
    result = validate_application_pack(pack_dir)
    if not result.get("ok"):
        raise SystemExit(f"application pack portability failure: {result}")
    for path in pack_dir.glob("*.json"):
        doc = json.loads(path.read_text())
        if doc.get("commit") in (None, "", "null"):
            raise SystemExit(f"commit null in {path}")
        if not doc.get("repository_url") and not doc.get("canonical_repository_url"):
            raise SystemExit(f"repository URL missing in {path}")
        blob = json.dumps(doc)
        if "/Users/" in blob or re.search(r'"commit"\s*:\s*null', blob):
            raise SystemExit(f"absolute path or null commit slipped into {path}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    oulu = oulu_pack()
    nva = nvidia_pack()
    write_json(OUT / "OULU_APPLICATION_EVIDENCE_PACK.json", oulu)
    write_json(OUT / "NVIDIA_APPLICATION_EVIDENCE_PACK.json", nva)
    (OUT / "OULU_APPLICATION_EVIDENCE_PACK.md").write_text(
        "# Oulu GENOME Application Evidence Pack\n\n"
        "Visibility/publication: `BLOCKED_USER_APPROVAL` / "
        "`REVIEWER_ACCESS_BLOCKED_USER_APPROVAL`\n\n"
        + json.dumps(oulu, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "NVIDIA_APPLICATION_EVIDENCE_PACK.md").write_text(
        "# NVIDIA Aerial Application Evidence Pack\n\n"
        "Visibility/publication: `BLOCKED_USER_APPROVAL` / "
        "`REVIEWER_ACCESS_BLOCKED_USER_APPROVAL`\n\n"
        + json.dumps(nva, indent=2)
        + "\n",
        encoding="utf-8",
    )
    # Sanitized reviewer bundle checklist (commands only — no auto-publish)
    (OUT / "PUBLICATION_HANDOFF.md").write_text(
        "# Publication / visibility handoff\n\n"
        "Status: `BLOCKED_USER_APPROVAL`\n\n"
        "Edmund must explicitly approve before any repository visibility change "
        "or public snapshot deposit.\n\n"
        "## Prepared commands (do not run without approval)\n\n"
        "```bash\n"
        "# gh repo edit gunnchOS3k/gunnchos-emergent-service-intent-protocols --visibility public\n"
        "# gh repo edit gunnchOS3k/gunnchos-gpu-nr-baseband-platform --visibility public\n"
        "```\n\n"
        "DOI remains `GATE5_DOI_PENDING` until an actual deposit exists.\n",
        encoding="utf-8",
    )
    _assert_portable(OUT)
    print(
        json.dumps(
            {
                "ok": True,
                "oulu": str(OUT / "OULU_APPLICATION_EVIDENCE_PACK.json"),
                "nvidia": str(OUT / "NVIDIA_APPLICATION_EVIDENCE_PACK.json"),
                "oulu_commit": oulu["commit"],
                "nvidia_commit": nva["commit"],
                "publication": "BLOCKED_USER_APPROVAL",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
