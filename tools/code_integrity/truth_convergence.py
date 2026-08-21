"""Truth-convergence validation and orphan methodology for Code Health Baseline V1."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from code_integrity.calibration import is_environment_path
except ImportError:  # pragma: no cover
    from calibration import is_environment_path  # type: ignore

ORPHAN_STATES = {
    "ACTIVE_PRODUCTION",
    "ACTIVE_DYNAMIC_ENTRY",
    "ACTIVE_CI_OR_EVIDENCE_PATH",
    "TEST_SUPPORT",
    "EVIDENCE_SUPPORT",
    "POSSIBLE_ORPHAN",
    "CONFIRMED_ORPHAN",
    "UNKNOWN_DYNAMIC_REACHABILITY",
}

# Known-active paths that must never be CONFIRMED_ORPHAN
KNOWN_ACTIVE_PATH_HINTS = [
    re.compile(r"sandbox_executor\.py$", re.I),
    re.compile(r"archive_life_pipeline/", re.I),
    re.compile(r"(^|/)vite\.config\.", re.I),
    re.compile(r"playwright", re.I),
    re.compile(r"readygary|beam.?select|digital_programme|sim/channels", re.I),
    re.compile(r"wave00[4-9]|Wave00[4-9]|engineering_wave00[4-9]", re.I),
]


def classify_orphan_candidate(
    rel: str,
    *,
    imported_names: set[str],
    text_hints: str = "",
    ci_blob: str = "",
    makefile_blob: str = "",
    package_json_blob: str = "",
    godot_blob: str = "",
) -> dict[str, Any]:
    """Expand orphan states; uncertain → UNKNOWN_DYNAMIC_REACHABILITY not CONFIRMED_ORPHAN."""
    if is_environment_path(rel):
        return {
            "path": rel,
            "state": "ACTIVE_PRODUCTION",  # excluded from orphan scoring elsewhere
            "excluded_environment": True,
            "reason": "VENDORED_OR_ENVIRONMENT",
        }

    stem = Path(rel).stem
    base = rel
    reasons = []

    # imports
    if stem in imported_names or stem.replace("-", "_") in imported_names:
        return {"path": rel, "state": "ACTIVE_PRODUCTION", "reason": "imported_by_name"}

    # CLI / package entry
    if re.search(rf"(^|/){re.escape(stem)}\b", package_json_blob) or '"bin"' in package_json_blob and stem in package_json_blob:
        return {"path": rel, "state": "ACTIVE_DYNAMIC_ENTRY", "reason": "package_json_reference"}

    if stem in makefile_blob or rel in makefile_blob:
        return {"path": rel, "state": "ACTIVE_CI_OR_EVIDENCE_PATH", "reason": "makefile_reference"}

    if stem in ci_blob or rel in ci_blob:
        return {"path": rel, "state": "ACTIVE_CI_OR_EVIDENCE_PATH", "reason": "ci_or_workflow_reference"}

    if ".gd" in rel or "godot" in rel.lower():
        if stem in godot_blob or rel in godot_blob:
            return {"path": rel, "state": "ACTIVE_DYNAMIC_ENTRY", "reason": "godot_reference"}

    # known active
    for rx in KNOWN_ACTIVE_PATH_HINTS:
        if rx.search(rel):
            return {
                "path": rel,
                "state": "ACTIVE_PRODUCTION",
                "reason": "known_active_code_pattern",
            }

    # test / evidence support paths
    if re.search(r"(^|/)(tests?|evals?|fixtures?|evidence)(/|$)", rel, re.I):
        return {"path": rel, "state": "TEST_SUPPORT", "reason": "proof_tree"}

    if re.search(r"(^|/)(artifacts?|reports?)(/|$)", rel, re.I):
        return {"path": rel, "state": "EVIDENCE_SUPPORT", "reason": "artifact_tree"}

    # plugin / dynamic load hints in nearby text
    if re.search(r"importlib|__import__|pkgutil|plugin|entry_points|load_module", text_hints, re.I):
        return {
            "path": rel,
            "state": "UNKNOWN_DYNAMIC_REACHABILITY",
            "reason": "dynamic_load_hint_nearby",
        }

    # Default: uncertain dynamic reachability — NEVER auto CONFIRMED_ORPHAN from name-miss alone
    return {
        "path": rel,
        "state": "UNKNOWN_DYNAMIC_REACHABILITY",
        "reason": "no_static_importer_found_not_confirmed",
    }


def refine_orphans_for_repo(
    candidates: list[str],
    *,
    imported_names: set[str],
    root_text_blobs: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    blobs = root_text_blobs or {}
    out = []
    for rel in candidates:
        if is_environment_path(rel):
            continue
        c = classify_orphan_candidate(
            rel,
            imported_names=imported_names,
            text_hints=blobs.get("text", ""),
            ci_blob=blobs.get("ci", ""),
            makefile_blob=blobs.get("makefile", ""),
            package_json_blob=blobs.get("package_json", ""),
            godot_blob=blobs.get("godot", ""),
        )
        out.append(c)
    return out


def filter_vendored_hotspots(hotspots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [h for h in hotspots if not is_environment_path(str(h.get("path", "")))]


def reconcile_proof_and_runtime(
    proof_status: str,
    still_coupled: list[str],
    runtime: dict[str, Any],
) -> dict[str, Any]:
    """Canonical proof independence is the worktree strip result.
    Runtime must NOT say FAIL_COUPLED / PRODUCTION_PROOF_COUPLING when proof is PASS_INDEPENDENT.
    """
    rt = dict(runtime)
    details = dict(rt.get("details") or {})
    gaps = [g for g in (details.get("gaps") or []) if g != "PRODUCTION_PROOF_COUPLING"]

    canonical = proof_status
    if proof_status == "PASS_INDEPENDENT" and not still_coupled:
        details["proof_independence_status"] = "PASS_INDEPENDENT"
        # Keep NEEDS_WORK for other real gaps (missing E2E etc.) but not coupling
        if rt.get("authenticity") == "NEEDS_WORK" and not gaps:
            # If the only reason was coupling, downgrade gap list honestly
            if not rt.get("has_entrypoint"):
                gaps.append("NO_ENTRYPOINT_DETECTED")
            elif not rt.get("has_tests"):
                gaps.append("NO_TESTS_DETECTED")
            else:
                # authenticity incomplete for reasons other than coupling — keep generic only if needed
                pass
        details["gaps"] = gaps
        # If authenticity was NEEDS_WORK solely due to coupling, recover ADEQUATE when entry+tests+prod
        if (
            rt.get("authenticity") == "NEEDS_WORK"
            and rt.get("has_entrypoint")
            and rt.get("has_tests")
            and not gaps
        ):
            rt["authenticity"] = "ADEQUATE"
    elif proof_status == "FAIL_COUPLED" or still_coupled:
        canonical = "FAIL_COUPLED"
        details["proof_independence_status"] = "FAIL_COUPLED"
        if "PRODUCTION_PROOF_COUPLING" not in gaps:
            gaps.append("PRODUCTION_PROOF_COUPLING")
        details["gaps"] = gaps
        if rt.get("authenticity") not in {"CRITICAL"}:
            rt["authenticity"] = "NEEDS_WORK"
    else:
        details["proof_independence_status"] = proof_status
        details["gaps"] = gaps

    rt["details"] = details
    rt["canonical_proof_independence"] = canonical
    return rt


def validate_truth_convergence(
    *,
    out_dir: Path,
    repo_count: int = 17,
    baseline_counts_changed: bool = False,
    requirement_states_changed: int = 0,
    other_repo_mutations: int = 0,
) -> dict[str, Any]:
    """Cross-output consistency validator."""
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": ok, "detail": detail})
        if not ok:
            failures.append(f"{name}: {detail}")

    def load(name: str) -> Any:
        p = out_dir / name
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))

    proof = load("PROOF_INDEPENDENCE_RESULTS.json") or {}
    runtime = load("RUNTIME_PATH_AUTHENTICITY_MATRIX.json") or {}
    dep = load("DEPENDENCY_BOUNDARY_ANALYSIS.json") or {}
    rem = load("REMEDIATION_REGISTER.json") or {}
    orphan = load("ORPHAN_DEAD_CODE.json") or {}
    hot = load("COMPLEXITY_HOTSPOTS.json") or {}
    mut = load("MUTATION_RESISTANCE_SAMPLES.json") or {}
    findings = load("FINDINGS.json") or {}
    baseline = load("BASELINE_RESULT.json") or {}
    prov = load("MUTATION_EXECUTION_PROVENANCE.json") or {}

    proof_map = {r.get("repository"): r for r in (proof.get("results") or [])}
    rt_map = {r.get("repository"): r for r in (runtime.get("repos") or [])}

    # 1) proof PASS + runtime FAIL_COUPLED
    contra = 0
    for repo, pr in proof_map.items():
        rr = rt_map.get(repo) or {}
        ps = pr.get("status")
        coupled = pr.get("still_coupled_production_files") or []
        rt_pi = rr.get("proof_independence")
        gaps = ((rr.get("authenticity") or {}).get("details") or {}).get("gaps") or []
        if ps == "PASS_INDEPENDENT" and not coupled:
            if rt_pi == "FAIL_COUPLED" or "PRODUCTION_PROOF_COUPLING" in gaps:
                contra += 1
    add(
        "PROOF_INDEPENDENCE_RUNTIME_MATRIX_CONTRADICTIONS",
        contra == 0,
        f"count={contra}",
    )

    # 2) R1 agreement
    r1_items = ((rem.get("families") or {}).get("R1") or {}).get("items") or []
    dep_coupled_repos = []
    for repo, info in (dep.get("repos") or {}).items():
        if (info.get("production_imports_proof") or 0) > 0 or info.get("dependency_boundaries") == "NEEDS_WORK":
            # only count as coupling if proof says FAIL
            if (proof_map.get(repo) or {}).get("status") == "FAIL_COUPLED":
                dep_coupled_repos.append(repo)
    proof_coupled = [r for r, p in proof_map.items() if p.get("status") == "FAIL_COUPLED"]
    r1_repos = sorted({i.get("repository") for i in r1_items})
    # Agreement: all three share same coupled set (possibly empty)
    coupled_set = sorted(set(proof_coupled))
    add(
        "R1_COUPLING_AGREEMENT",
        set(r1_repos) == set(coupled_set) and set(dep_coupled_repos) <= set(coupled_set),
        f"proof={coupled_set} r1={r1_repos} dep={dep_coupled_repos}",
    )

    # 3) known active as orphan
    known_active_orphan = 0
    orphan_remaining = []
    for repo, entries in (orphan.get("repos") or {}).items():
        for e in entries:
            if isinstance(e, str):
                path, state = e, "UNKNOWN_DYNAMIC_REACHABILITY"
            else:
                path, state = e.get("path", ""), e.get("state", "")
            if state == "CONFIRMED_ORPHAN":
                for rx in KNOWN_ACTIVE_PATH_HINTS:
                    if rx.search(path):
                        known_active_orphan += 1
                orphan_remaining.append({"repository": repo, "path": path, "state": state})
            if path.endswith("sandbox_executor.py") and state == "CONFIRMED_ORPHAN":
                known_active_orphan += 1
    add("KNOWN_ACTIVE_CODE_CLASSIFIED_ORPHAN", known_active_orphan == 0, f"count={known_active_orphan}")

    # 4) vendored hotspots / critical
    vendored_hot = 0
    vendored_crit = 0
    for repo, spots in (hot.get("repos") or {}).items():
        for h in spots or []:
            p = str(h.get("path", ""))
            if is_environment_path(p):
                vendored_hot += 1
                if (h.get("complexity") or 0) >= 40:
                    vendored_crit += 1
    add("VENDORED_ENVIRONMENT_COMPLEXITY_HOTSPOTS", vendored_hot == 0, f"count={vendored_hot}")
    add("VENDORED_ENVIRONMENT_CRITICAL_FINDINGS", vendored_crit == 0, f"count={vendored_crit}")

    # 5) mutation survival without executed tests
    bad_surv = 0
    for r in mut.get("results") or []:
        if r.get("mutation_outcome") == "MUTATION_SURVIVED":
            for m in r.get("mutations") or []:
                if m.get("mutation_outcome") == "MUTATION_SURVIVED":
                    if not (
                        m.get("full_run_executed")
                        and m.get("baseline_passed") is True
                        and m.get("mutated_passed") is True
                        and m.get("behavioral")
                        and m.get("kind") != "append_marker"
                    ):
                        bad_surv += 1
            # also reject aggregate survival if any mutation used forbidden reactions
            for m in r.get("mutations") or []:
                if m.get("test_reaction") in {
                    "COLLECTION_STILL_OK_FULL_RUN_NOT_EXECUTED",
                    "MARKER_LIKELY_UNDETECTED",
                    "NO_TESTS_DIR",
                } and m.get("mutation_outcome") == "MUTATION_SURVIVED":
                    bad_surv += 1
    add("MUTATION_SURVIVAL_REQUIRES_EXECUTED_TESTS", bad_surv == 0, f"bad={bad_surv}")

    # 6) S0/S1 reachability/capability
    weak = 0
    for f in findings.get("findings") or []:
        if f.get("severity") not in {"S0", "S1"}:
            continue
        reach = f.get("reachability") or {}
        if not reach.get("active"):
            weak += 1
        if f.get("severity") == "S0" and not (f.get("capability_closure") or {}).get("all_five", True):
            # if closure present and not all five
            if f.get("capability_closure") and not f["capability_closure"].get("all_five"):
                weak += 1
    add("S0_S1_REACHABILITY_CAPABILITY", weak == 0, f"weak={weak}")

    # 7) duplicate root-cause counts
    keys = []
    for f in findings.get("findings") or []:
        if f.get("severity") in {"S0", "S1"}:
            keys.append((f.get("repository"), f.get("family"), f.get("kind"), f.get("path")))
    dup = len(keys) - len(set(keys))
    add("DUPLICATE_ROOT_CAUSE_COUNTS", dup == 0, f"dup={dup}")

    # 8) baseline / repo counts
    add("CANONICAL_REPOS_AUDITED", repo_count == 17, f"count={repo_count}")
    add("BASELINE_COUNTS_CHANGED", baseline_counts_changed is False, str(baseline_counts_changed))
    add("REQUIREMENT_STATES_CHANGED", requirement_states_changed == 0, str(requirement_states_changed))
    add("OTHER_REPO_MUTATIONS", other_repo_mutations == 0, str(other_repo_mutations))

    # mutation classifier controls + provenance
    ctrl_pass = False
    if prov and prov.get("MUTATION_CLASSIFIER_CONTROLS_PASS") is True:
        ctrl_pass = True
    elif (baseline.get("controls") or {}).get("mutation_classifier_controls", {}).get(
        "MUTATION_CLASSIFIER_CONTROLS_PASS"
    ) is True:
        ctrl_pass = True
    add("MUTATION_CLASSIFIER_CONTROLS_PASS", ctrl_pass, str(ctrl_pass))
    add("MUTATION_EXECUTION_PROVENANCE_PRESENT", bool(prov), "missing" if not prov else "ok")

    passed = len(failures) == 0

    token = (
        "CODE_HEALTH_BASELINE_V1_TRUTH_CONVERGENCE_VALIDATION_PASS"
        if passed
        else "CODE_HEALTH_BASELINE_V1_TRUTH_CONVERGENCE_VALIDATION_FAIL"
    )
    result = {
        "generated_at_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "CODE_HEALTH_BASELINE_V1_TRUTH_CONVERGENCE_VALIDATION": "PASS" if passed else "FAIL",
        "CODE_HEALTH_BASELINE_V1_TRUTH_CONVERGENCE_VALIDATION_PASS": passed,
        "token": token,
        "PROOF_INDEPENDENCE_RUNTIME_MATRIX_CONTRADICTIONS": contra,
        "KNOWN_ACTIVE_CODE_CLASSIFIED_ORPHAN": known_active_orphan,
        "VENDORED_ENVIRONMENT_COMPLEXITY_HOTSPOTS": vendored_hot,
        "VENDORED_ENVIRONMENT_CRITICAL_FINDINGS": vendored_crit,
        "PRODUCTION_PROOF_COUPLING_ROOT_CAUSES": coupled_set,
        "CANONICAL_REPOS_AUDITED": repo_count,
        "BASELINE_COUNTS_CHANGED": baseline_counts_changed,
        "REQUIREMENT_STATES_CHANGED": requirement_states_changed,
        "OTHER_REPO_MUTATIONS": other_repo_mutations,
        "checks": checks,
        "failures": failures,
        "remaining_confirmed_orphans": orphan_remaining[:40],
    }
    return result
