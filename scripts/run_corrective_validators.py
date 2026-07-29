#!/usr/bin/env python3
"""Completion validators for Gates 4–6 — requirement completion, not mere execution."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_inherited_ci import evaluate as evaluate_deps  # noqa: E402

REPOS = ROOT.parent
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|PLACEHOLDER|commit:\s*null|/Users/)\b", re.I)


def _commit(repo: Path) -> str:
    import subprocess

    try:
        return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def validate_oulu_scientific(manifest_path: Path | None = None) -> dict:
    oulu = REPOS / "gunnchos-emergent-service-intent-protocols"
    pending = [
        "OULU_ENV_CAUSALITY_PENDING",
        "OULU_DIAL_FIDELITY_PENDING",
        "OULU_QMIX_FIDELITY_PENDING",
        "OULU_BASELINE_MATRIX_INCOMPLETE",
        "OULU_GENERALIZATION_INCOMPLETE",
        "OULU_ROBUSTNESS_INCOMPLETE",
        "OULU_STATISTICS_INCOMPLETE",
        "OULU_INTERPRETABILITY_INCOMPLETE",
        "OULU_MANUSCRIPT_RESULTS_INCOMPLETE",
    ]
    smoke_ok = (oulu / "Makefile").exists()
    causal = list(oulu.glob("tests/**/*causal*")) + list(oulu.glob("tests/**/*comm*"))
    final_dir = oulu / "results" / "final"
    gen_dir = oulu / "results" / "generalization"
    figs = list((oulu / "paper" / "figures").glob("*")) if (oulu / "paper" / "figures").exists() else []
    scientific_ready = False
    reasons = []
    if not causal:
        reasons.append("causal_tests_missing")
    if not final_dir.exists() or not any(final_dir.rglob("*.json")):
        reasons.append("final_results_missing")
        pending.append("GATE4_OULU_SCIENTIFIC_EVIDENCE_PENDING")
    if not gen_dir.exists():
        reasons.append("generalization_missing")
    if not figs:
        reasons.append("figures_missing")
    # Smoke alone cannot earn scientific PASS
    status = (
        "GATE4_OULU_SCIENTIFIC_EVIDENCE_PASS"
        if scientific_ready
        else ("GATE4_OULU_FUNCTIONAL_SCAFFOLD_PASS" if smoke_ok else "GATE4_OULU_SCIENTIFIC_EVIDENCE_PENDING")
    )
    if status == "GATE4_OULU_FUNCTIONAL_SCAFFOLD_PASS":
        reasons.append("smoke_or_scaffold_only_not_scientific_pass")
    manifest = {
        "schema_version": "1.0.0",
        "environment_version": "corrective-depth",
        "repository_commit": _commit(oulu),
        "causal_communication_tests": {"ok": bool(causal), "paths": [str(p) for p in causal[:20]]},
        "control_action_effect_tests": {"ok": False, "pending": True},
        "algorithm_fidelity_tests": {"ok": False, "pending": True},
        "algorithms_implemented": [],
        "baseline_matrix": {"complete": False},
        "scenario_matrix": {"complete": False},
        "abstraction_matrix": {"complete": False},
        "objective_matrix": {"complete": False},
        "seed_matrix": {"min_seeds_required": 5, "complete": False},
        "generalization_matrix": {"complete": False},
        "robustness_matrix": {"complete": False},
        "interpretability_outputs": {"complete": False},
        "statistical_outputs": {"complete": False},
        "generated_figures": [str(p) for p in figs],
        "generated_tables": [],
        "raw_result_checksums": {},
        "paper_result_references": [],
        "clean_reproduction_report": {"ok": False, "pending": True},
        "status": status,
        "pending_states": pending,
        "notes": reasons,
    }
    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "ok": status == "GATE4_OULU_SCIENTIFIC_EVIDENCE_PASS",
        "status": status,
        "manifest": manifest,
        "scientific_denied_if_smoke_only": True,
    }


def validate_nvidia_aerial_depth(manifest_path: Path | None = None) -> dict:
    nv = REPOS / "gunnchos-gpu-nr-baseband-platform"
    educational_only = True
    edu = (nv / "educational").exists()
    # Detect educational-only LDPC markers without claiming PASS
    src_text = ""
    for p in nv.glob("**/*ldpc*"):
        if p.is_file() and p.suffix in {".hpp", ".cpp", ".h", ".cc", ".md"}:
            try:
                src_text += p.read_text(errors="ignore")[:5000]
            except Exception:
                pass
    if "BG1" in src_text or "bg1" in src_text.lower() or "lifting" in src_text.lower():
        educational_only = False
    cuda_sources = list(nv.glob("**/*.cu")) + list(nv.glob("**/cuda/**/*.cpp"))
    cuda_correctness = list(nv.glob("**/results/**/*cuda*correct*")) + list(
        nv.glob("**/results/**/cuda_*.json")
    )
    gpu_numeric_forbidden = False
    # Reject numeric GPU results on non-NVIDIA hosts if host marker present
    for p in nv.glob("**/results/**/*.json"):
        try:
            doc = json.loads(p.read_text())
        except Exception:
            continue
        if doc.get("gpu_throughput") or doc.get("gpu_p99_us"):
            if doc.get("hardware", {}).get("nvidia_gpu_present") is False:
                gpu_numeric_forbidden = True
    status = "GATE4_NVIDIA_AERIAL_DEPTH_PENDING"
    if edu and educational_only:
        status = "GATE4_NVIDIA_EDUCATIONAL_CPU_PASS"
    if cuda_sources and not cuda_correctness:
        # CUDA source without correctness => deny CUDA ready
        pending_cuda = True
    else:
        pending_cuda = False
    if educational_only:
        aerial_denied = True
    else:
        aerial_denied = True  # still pending until full matrix
        status = "GATE4_NVIDIA_AERIAL_DEPTH_PENDING"
    manifest = {
        "schema_version": "1.0.0",
        "repository_commit": _commit(nv),
        "standards_traceable_nr_path": {"ok": not educational_only},
        "external_reference_vectors": {"ok": False},
        "nr_ldpc_path": {"educational_only": educational_only},
        "exact_modulation": {"ok": False},
        "usable_soft_llr": {"ok": False},
        "scrambling_and_rate_matching": {"ok": False},
        "configurable_ofdm_numerology": {"ok": False},
        "channel_estimation_and_mimo": {"ok": False},
        "scheduler_depth": {"ok": False},
        "cuda_baseband_components": {
            "sources": len(cuda_sources),
            "correctness_evidence": len(cuda_correctness),
            "ready": bool(cuda_sources) and bool(cuda_correctness) and not pending_cuda,
        },
        "cpu_gpu_orchestration": {"ok": False},
        "real_time_deadline_model": {"ok": False},
        "fault_handling": {"ok": False},
        "profiling_harness": {"ok": False},
        "controlled_optimization_studies": {"count": 0, "ok": False},
        "fapi_fronthaul_validation": {"ok": False},
        "upstream_contribution": {"status": "DOCUMENTED_IMPLEMENTATION_PENDING"},
        "ci_quality": {"ok": False},
        "clean_reproduction": {"ok": False},
        "educational_path_separated": edu,
        "status": status if not gpu_numeric_forbidden else "BLOCKED_HARDWARE",
        "pending_states": ["GATE4_NVIDIA_GPU_MEASUREMENT_PENDING", "GATE4_NVIDIA_AERIAL_DEPTH_PENDING"],
        "notes": [
            "Aerial-depth PASS denied while educational-only path dominates",
            "GPU numeric results forbidden without NVIDIA hardware evidence",
        ],
    }
    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "ok": status == "GATE4_NVIDIA_AERIAL_DEPTH_PASS",
        "status": manifest["status"],
        "manifest": manifest,
        "aerial_denied": aerial_denied or educational_only,
        "gpu_numeric_forbidden": gpu_numeric_forbidden,
    }


def validate_gate5_publication() -> dict:
    blockers = []
    for paper in [
        REPOS / "gunnchos-emergent-service-intent-protocols" / "paper" / "RESOURCE_EFFICIENT_EMERGENT_SERVICE_INTENT_PROTOCOLS.md",
        REPOS / "gunnchos-gpu-nr-baseband-platform" / "paper" / "CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
    ]:
        if not paper.is_file():
            blockers.append(f"missing_paper:{paper.name}")
            continue
        text = paper.read_text(encoding="utf-8", errors="ignore")
        if PLACEHOLDER_RE.search(text):
            blockers.append(f"placeholders:{paper.name}")
        if "Bibliography" not in text and "References" not in text:
            blockers.append(f"bibliography_absent:{paper.name}")
    figs_missing = not any(
        (REPOS / "gunnchos-emergent-service-intent-protocols" / "paper").glob("**/figures/**")
    )
    if figs_missing:
        blockers.append("figures_absent")
    status = "GATE5_DRAFT_PACKAGE_PASS" if not blockers else "GATE5_PUBLICATION_RELEASE_PENDING"
    if blockers:
        status = "GATE5_PUBLICATION_RELEASE_PENDING"
    return {
        "ok": status == "GATE5_RELEASE_CANDIDATE_PASS",
        "status": status,
        "blockers": blockers,
        "independent_reproduction": "GATE5_INDEPENDENT_REPRODUCTION_PENDING",
        "doi_status": "GATE5_DOI_PENDING",
    }


def validate_application_pack(pack_dir: Path) -> dict:
    errors = []
    for path in pack_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".md", ".yml", ".yaml", ".txt", ".cff"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "/Users/" in text:
            errors.append(f"absolute_local_path:{path}")
        if re.search(r'"commit"\s*:\s*null', text):
            errors.append(f"commit_null:{path}")
        if "publicly accessible" in text.lower() and "private" in text.lower():
            # heuristic only
            pass
    return {"ok": not errors, "errors": errors}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--track",
        choices=[
            "oulu-scientific",
            "nvidia-aerial-depth",
            "gate5-publication-release",
            "gate6-harness",
            "application-evidence-pack",
            "corrective-audit",
            "all-corrective",
        ],
        required=True,
    )
    args = p.parse_args(argv)
    out = ROOT / "orchestration" / "gates_4_6" / "corrective"
    out.mkdir(parents=True, exist_ok=True)

    if args.track == "corrective-audit":
        result = {
            "ok": (ROOT / "CORRECTIVE_DEPTH_INITIAL_AUDIT.md").exists()
            and (ROOT / "CORRECTIVE_DEPTH_FAILURE_REPRODUCTION.md").exists(),
            "status": "CONTROL_PLANE_IMPLEMENTED_BUT_CI_RED",
        }
    elif args.track == "oulu-scientific":
        result = validate_oulu_scientific(out / "oulu_scientific_evidence_manifest.json")
    elif args.track == "nvidia-aerial-depth":
        result = validate_nvidia_aerial_depth(out / "nvidia_aerial_depth_manifest.json")
    elif args.track == "gate5-publication-release":
        result = validate_gate5_publication()
    elif args.track == "gate6-harness":
        # Delegate to dry-run script
        import subprocess

        rc = subprocess.call([sys.executable, str(ROOT / "scripts" / "run_gate6_dry_run.py")])
        result = {
            "ok": rc == 0,
            "status": "GATE6_PARTIAL_HARNESS_PASS" if rc == 0 else "GATE6_HARNESS_FAIL",
            "physical": "GATE6_PHYSICAL_EVIDENCE_PENDING",
        }
    elif args.track == "application-evidence-pack":
        pack = ROOT / "application_evidence"
        result = validate_application_pack(pack) if pack.exists() else {"ok": False, "errors": ["missing_pack"]}
    else:
        results = {
            "oulu": validate_oulu_scientific(out / "oulu_scientific_evidence_manifest.json"),
            "nvidia": validate_nvidia_aerial_depth(out / "nvidia_aerial_depth_manifest.json"),
            "gate5": validate_gate5_publication(),
        }
        result = {
            "ok": False,
            "status": "CONTROL_PLANE_IMPLEMENTED_BUT_CI_RED",
            "parts": {k: v.get("status") for k, v in results.items()},
            "non_claims": [
                "NO_ACCEPTANCE_GUARANTEE",
                "NVIDIA_TENURE_REQUIREMENT_UNSATISFIED",
                "NVIDIA_CUSTOMER_TRIAL_REQUIREMENT_PENDING",
                "GATE4_OULU_SCIENTIFIC_EVIDENCE_PENDING",
                "GATE4_NVIDIA_AERIAL_DEPTH_PENDING",
                "GATE5_PUBLICATION_RELEASE_PENDING",
                "GATE6_PHYSICAL_EVIDENCE_PENDING",
            ],
        }
    (out / f"{args.track}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    # Completion validators return 0 when the validator itself ran correctly;
    # scientific PASS is reflected in result["ok"], not necessarily exit code,
    # except for gate6-harness which must fail closed.
    if args.track == "gate6-harness":
        return 0 if result.get("ok") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
