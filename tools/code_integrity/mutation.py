"""Mutation-evidence semantics for Code Health Baseline V1.

Precise outcomes only:
  MUTATION_KILLED / MUTATION_SURVIVED / MUTATION_TEST_NOT_EXECUTED /
  MUTATION_VALIDATION_INCOMPLETE / NO_RELEVANT_TEST_HARNESS_FOUND /
  NO_EXECUTABLE_TEST_COVERAGE / BLOCKED_ENVIRONMENT /
  INVALID_MUTATION_SAMPLE / AUDIT_INCONCLUSIVE

Collection-only, MARKER_LIKELY_UNDETECTED, NO_TESTS_DIR, and append_marker
are NEVER survival.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

MUTATION_CLASSIFIER_FLAGS = {
    "FULL_TEST_RUN_REQUIRED_FOR_MUTATION_SURVIVAL": True,
    "COLLECTION_ONLY_NOT_SURVIVAL": True,
    "LIKELY_UNDETECTED_NOT_SURVIVAL": True,
    "NO_TESTS_DIR_NOT_SURVIVAL": True,
    "BEHAVIORAL_MUTATION_REQUIRED": True,
    "MARKER_MUTATIONS_COUNT_AS_SURVIVAL": False,
    "MUTATION_SURVIVAL_REQUIRES_EXECUTED_RELEVANT_TESTS": True,
    "APPEND_MARKER_REQUIRES_BEHAVIORAL_EFFECT": True,
}

BEHAVIORAL_KINDS = {
    "flip_return_true",
    "flip_return_false",
    "flip_return_zero",
    "invert_condition",
    "remove_validation",
    "change_metric",
}

NON_SURVIVAL_REACTIONS = {
    "COLLECTION_STILL_OK_FULL_RUN_NOT_EXECUTED",
    "MARKER_LIKELY_UNDETECTED",
    "NO_TESTS_DIR",
    "UNKNOWN",
    "COLLECTION_ONLY",
}

R5_FOCUS = {
    "gunnchos-research-portal",
    "7gc-digital-twin",
    "readygary-6g-beam-selection",
    "waike-research-ops",
    "gunnchos-emergent-service-intent-protocols",
}


def run_mutation_classifier_controls() -> dict[str, Any]:
    """Self-controls: collection≠survived, marker≠survived, no-tests≠survived,
    baseline fail→inconclusive, real behavioral+pass→survived, real+fail→killed.
    """
    cases = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        cases.append({"name": name, "pass": ok, "detail": detail})

    # collection-only must not be survival
    check(
        "collection_only_not_survived",
        classify_mutation_outcome(
            baseline_pass=True,
            mutated_pass=True,
            full_run_executed=False,
            collection_only=True,
            behavioral=True,
            mutation_kind="flip_return_true",
            mutation_verified_present=True,
        )
        != "MUTATION_SURVIVED",
    )
    # marker must not be survival
    check(
        "marker_not_survived",
        classify_mutation_outcome(
            baseline_pass=True,
            mutated_pass=True,
            full_run_executed=True,
            collection_only=False,
            behavioral=False,
            mutation_kind="append_marker",
            mutation_verified_present=True,
        )
        != "MUTATION_SURVIVED",
    )
    # no-tests must not be survival
    check(
        "no_tests_not_survived",
        classify_mutation_outcome(
            baseline_pass=None,
            mutated_pass=None,
            full_run_executed=False,
            collection_only=False,
            behavioral=True,
            mutation_kind="flip_return_true",
            mutation_verified_present=True,
            no_harness=True,
        )
        != "MUTATION_SURVIVED",
    )
    # baseline fail → inconclusive
    check(
        "baseline_fail_inconclusive",
        classify_mutation_outcome(
            baseline_pass=False,
            mutated_pass=False,
            full_run_executed=True,
            collection_only=False,
            behavioral=True,
            mutation_kind="flip_return_true",
            mutation_verified_present=True,
        )
        in {"MUTATION_VALIDATION_INCOMPLETE", "AUDIT_INCONCLUSIVE"},
    )
    # real behavioral + pass → survived
    check(
        "behavioral_pass_survived",
        classify_mutation_outcome(
            baseline_pass=True,
            mutated_pass=True,
            full_run_executed=True,
            collection_only=False,
            behavioral=True,
            mutation_kind="flip_return_true",
            mutation_verified_present=True,
        )
        == "MUTATION_SURVIVED",
    )
    # real behavioral + fail → killed
    check(
        "behavioral_fail_killed",
        classify_mutation_outcome(
            baseline_pass=True,
            mutated_pass=False,
            full_run_executed=True,
            collection_only=False,
            behavioral=True,
            mutation_kind="flip_return_true",
            mutation_verified_present=True,
        )
        == "MUTATION_KILLED",
    )

    passed = all(c["pass"] for c in cases)
    return {
        "MUTATION_CLASSIFIER_CONTROLS_PASS": passed,
        "flags": dict(MUTATION_CLASSIFIER_FLAGS),
        "cases": cases,
    }


def classify_mutation_outcome(
    *,
    baseline_pass: bool | None,
    mutated_pass: bool | None,
    full_run_executed: bool,
    collection_only: bool,
    behavioral: bool,
    mutation_kind: str,
    mutation_verified_present: bool,
    no_harness: bool = False,
    blocked_env: bool = False,
    invalid_sample: bool = False,
) -> str:
    if invalid_sample:
        return "INVALID_MUTATION_SAMPLE"
    if blocked_env:
        return "BLOCKED_ENVIRONMENT"
    if no_harness:
        return "NO_RELEVANT_TEST_HARNESS_FOUND"
    if mutation_kind == "append_marker" or not behavioral:
        # Marker alone never survival; without behavioral effect → incomplete/invalid
        if full_run_executed and baseline_pass and mutated_pass and mutation_verified_present:
            return "INVALID_MUTATION_SAMPLE"
        return "MUTATION_TEST_NOT_EXECUTED" if not full_run_executed else "INVALID_MUTATION_SAMPLE"
    if collection_only or not full_run_executed:
        return "MUTATION_TEST_NOT_EXECUTED"
    if baseline_pass is False:
        return "MUTATION_VALIDATION_INCOMPLETE"
    if baseline_pass is None or mutated_pass is None:
        return "AUDIT_INCONCLUSIVE"
    if not mutation_verified_present:
        return "INVALID_MUTATION_SAMPLE"
    if baseline_pass and mutated_pass is False:
        return "MUTATION_KILLED"
    if baseline_pass and mutated_pass:
        return "MUTATION_SURVIVED"
    return "AUDIT_INCONCLUSIVE"


def discover_test_command(wt: Path) -> dict[str, Any]:
    """Find a repo-native full relevant suite command (not collect-only)."""
    makefile = wt / "Makefile"
    if makefile.exists():
        text = makefile.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^test\s*:", text, re.M):
            return {
                "command": ["make", "test"],
                "source": "Makefile:test",
                "full_run": True,
            }
    pyproject = wt / "pyproject.toml"
    if (wt / "tests").is_dir() or (wt / "test").is_dir() or (wt / "pytest.ini").exists() or pyproject.exists():
        cmd = [sys.executable, "-m", "pytest", "-q"]
        if (wt / "src").is_dir():
            # common layout
            env_note = "PYTHONPATH=src:."
        else:
            env_note = "PYTHONPATH=."
        return {
            "command": cmd,
            "source": "pytest",
            "full_run": True,
            "env_note": env_note,
        }
    pkg = wt / "package.json"
    if pkg.exists():
        try:
            import json

            scripts = (json.loads(pkg.read_text(encoding="utf-8")).get("scripts") or {})
            for key in ("test", "test:unit", "test:ci"):
                if key in scripts:
                    return {
                        "command": ["npm", "test", "--if-present"] if key == "test" else ["npm", "run", key],
                        "source": f"package.json:{key}",
                        "full_run": True,
                    }
        except Exception:
            pass
    return {"command": None, "source": None, "full_run": False}


def _run_suite(wt: Path, cmd: list[str], timeout: int = 300) -> dict[str, Any]:
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    # Prefer local src on path for pytest invocations
    pp = env.get("PYTHONPATH", "")
    extras = []
    if (wt / "src").is_dir():
        extras.append(str(wt / "src"))
    extras.append(str(wt))
    env["PYTHONPATH"] = ":".join(extras + ([pp] if pp else []))
    try:
        pr = subprocess.run(
            cmd,
            cwd=str(wt),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "returncode": pr.returncode,
            "passed": pr.returncode == 0,
            "stdout_tail": (pr.stdout or "")[-1500:],
            "stderr_tail": (pr.stderr or "")[-1500:],
            "executed": True,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "passed": False,
            "stdout_tail": "",
            "stderr_tail": "TIMEOUT",
            "executed": True,
            "blocked": True,
        }
    except Exception as e:
        return {
            "returncode": -1,
            "passed": False,
            "stdout_tail": "",
            "stderr_tail": str(e)[:400],
            "executed": False,
            "blocked": True,
        }


def _apply_behavioral_mutation(text: str) -> tuple[str, str] | None:
    """Return (mutated, kind) for a meaningful behavioral change, or None."""
    if "return True" in text:
        return text.replace("return True", "return False", 1), "flip_return_true"
    if "return False" in text:
        return text.replace("return False", "return True", 1), "flip_return_false"
    if re.search(r"return\s+0\b", text):
        return re.sub(r"return\s+0\b", "return 1", text, count=1), "flip_return_zero"
    # invert a simple comparison used in validation
    m = re.search(r"if\s+(.+?)\s*==\s*(.+?):", text)
    if m:
        mutated = text[: m.start()] + f"if {m.group(1)} != {m.group(2)}:" + text[m.end() :]
        return mutated, "invert_condition"
    # remove a raise ValidationError / ValueError guard (first occurrence)
    m2 = re.search(r"\n(\s+)raise\s+(ValueError|ValidationError|AssertionError)\b[^\n]*\n", text)
    if m2:
        mutated = text[: m2.start()] + "\n" + m2.group(1) + "pass  # CHAB_REMOVED_VALIDATION\n" + text[m2.end() :]
        return mutated, "remove_validation"
    # change a metric multiplier / threshold
    m3 = re.search(r"(threshold|margin|score|accuracy|precision)\s*=\s*([0-9]+\.?[0-9]*)", text, re.I)
    if m3:
        try:
            val = float(m3.group(2))
            new = 0.0 if val != 0 else 1.0
            mutated = text[: m3.start()] + f"{m3.group(1)} = {new}" + text[m3.end() :]
            return mutated, "change_metric"
        except Exception:
            pass
    return None


def _candidate_targets(wt: Path, classify_path, iter_files, max_n: int = 8) -> list[Path]:
    """Prefer production modules that tests likely import."""
    preferred = [
        "scripts/validate_supervisor_ready.py",
        "src/seven_gc_twin/scene/osm_overpass.py",
        "sim/experiments/digital_programme.py",
        "src/waike_curriculum/evaluation/metrics.py",
        "src/emergent_intent/algorithms/trainers.py",
        "src/emergent_intent/env/wireless_env.py",
    ]
    scored: list[tuple[int, Path]] = []
    test_blob = ""
    for tdir in ("tests", "test"):
        d = wt / tdir
        if d.is_dir():
            for p in d.rglob("*.py"):
                try:
                    test_blob += p.read_text(encoding="utf-8", errors="replace")[:5000]
                except Exception:
                    pass
    # Boost preferred paths first when present + mutable
    for pref in preferred:
        pp = wt / pref
        if pp.exists() and pp.is_file():
            text = pp.read_text(encoding="utf-8", errors="replace")
            if _apply_behavioral_mutation(text) is not None:
                scored.append((100, pp))
    for path in iter_files(wt):
        rel = path.relative_to(wt).as_posix()
        if path.suffix != ".py":
            continue
        if any(s[1] == path for s in scored):
            continue
        cls = classify_path(rel)
        if cls != "PRODUCTION":
            # allow scripts used by make test
            if not rel.startswith("scripts/"):
                continue
        if any(x in rel for x in (".venv", "site-packages", "node_modules", "vendor")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if _apply_behavioral_mutation(text) is None:
            continue
        stem = path.stem
        score = 0
        if stem and stem in test_blob:
            score += 5
        if "/src/" in f"/{rel}/" or rel.startswith("src/"):
            score += 2
        if "scripts/" in rel:
            score += 3
        scored.append((score, path))
    scored.sort(key=lambda x: (-x[0], x[1].as_posix()))
    return [p for _, p in scored[:max_n]]


def mutation_sample_calibrated(
    name: str,
    root: Path,
    sha: str,
    *,
    classify_path,
    iter_files,
    deep: bool = False,
) -> dict[str, Any]:
    """Run calibrated mutation evidence. deep=True for R5 focus (full suite)."""
    out: dict[str, Any] = {
        "repository": name,
        "sha": sha,
        "mutations": [],
        "status": "NOT_RUN",
        "dimension": "NOT_APPLICABLE",
        "mutation_outcome": "MUTATION_TEST_NOT_EXECUTED",
        "flags": dict(MUTATION_CLASSIFIER_FLAGS),
        "provenance": {
            "repository": name,
            "sha": sha,
            "test_command": None,
            "baseline": None,
            "mutated_runs": [],
            "worktree_mode": "temp_detached_discarded",
        },
    }
    if not root.exists():
        out["status"] = "SKIP_MISSING"
        out["mutation_outcome"] = "BLOCKED_ENVIRONMENT"
        return out

    tmp = Path(tempfile.mkdtemp(prefix=f"mut_{name}_"))
    try:
        wt = tmp / "wt"
        r = subprocess.run(
            ["git", "worktree", "add", "--detach", str(wt), sha],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=180,
        )
        if not wt.exists():
            out["status"] = "SKIP_WORKTREE_FAILED"
            out["mutation_outcome"] = "BLOCKED_ENVIRONMENT"
            out["stderr"] = (r.stderr or "")[:300]
            return out

        harness = discover_test_command(wt)
        out["provenance"]["test_command"] = {
            "argv": harness.get("command"),
            "source": harness.get("source"),
            "full_run": harness.get("full_run"),
        }
        if not harness.get("command"):
            out["status"] = "SAMPLED"
            out["mutation_outcome"] = "NO_RELEVANT_TEST_HARNESS_FOUND"
            out["dimension"] = "NEEDS_WORK" if deep else "NEEDS_WORK"
            # still record attempted target discovery for audit
            targets = _candidate_targets(wt, classify_path, iter_files, max_n=1)
            if targets:
                out["mutations"].append(
                    {
                        "index": 1,
                        "path": targets[0].relative_to(wt).as_posix(),
                        "kind": "behavioral_candidate_unexecuted",
                        "syntax_ok_after_mutation": True,
                        "test_reaction": "NO_RELEVANT_TEST_HARNESS_FOUND",
                        "mutation_outcome": "NO_RELEVANT_TEST_HARNESS_FOUND",
                        "behavioral": True,
                        "full_run_executed": False,
                    }
                )
            return out

        # Baseline: full suite only for deep (R5) calibration; else do not claim survival
        if deep:
            baseline = _run_suite(wt, harness["command"], timeout=420)
        else:
            # Non-R5: record harness presence without claiming survival from collection-only
            baseline = {
                "returncode": None,
                "passed": None,
                "executed": False,
                "blocked": False,
                "note": "full_run_deferred_non_r5",
            }
        out["provenance"]["baseline"] = {
            "returncode": baseline.get("returncode"),
            "passed": baseline.get("passed"),
            "executed": baseline.get("executed"),
            "blocked": baseline.get("blocked", False),
            "note": baseline.get("note"),
        }
        if baseline.get("blocked"):
            out["status"] = "SAMPLED"
            out["mutation_outcome"] = "BLOCKED_ENVIRONMENT"
            out["dimension"] = "BLOCKED"
            return out

        targets = _candidate_targets(wt, classify_path, iter_files, max_n=3 if deep else 1)
        if not targets:
            out["status"] = "NO_MUTATION_TARGETS"
            out["mutation_outcome"] = "INVALID_MUTATION_SAMPLE"
            out["dimension"] = "NOT_APPLICABLE"
            return out

        if not deep:
            # Honest non-survival label: harness exists but full R5-style run not executed here
            path = targets[0]
            rel = path.relative_to(wt).as_posix()
            original = path.read_text(encoding="utf-8", errors="replace")
            applied = _apply_behavioral_mutation(original)
            if not applied:
                out["status"] = "NO_MUTATION_TARGETS"
                out["mutation_outcome"] = "INVALID_MUTATION_SAMPLE"
                out["dimension"] = "NOT_APPLICABLE"
                return out
            mutated, kind = applied
            out["mutations"].append(
                {
                    "index": 1,
                    "path": rel,
                    "kind": kind,
                    "syntax_ok_after_mutation": True,
                    "behavioral": True,
                    "mutation_verified_present": False,
                    "full_run_executed": False,
                    "collection_only": False,
                    "baseline_passed": None,
                    "mutated_passed": None,
                    "test_reaction": "MUTATION_TEST_NOT_EXECUTED",
                    "mutation_outcome": "MUTATION_TEST_NOT_EXECUTED",
                }
            )
            out["status"] = "SAMPLED"
            out["mutation_outcome"] = "MUTATION_TEST_NOT_EXECUTED"
            out["dimension"] = "NEEDS_WORK"
            out["detected_count"] = 0
            out["survived_count"] = 0
            return out

        killed = 0
        survived = 0
        outcomes: list[str] = []

        for i, path in enumerate(targets):
            rel = path.relative_to(wt).as_posix()
            original = path.read_text(encoding="utf-8", errors="replace")
            applied = _apply_behavioral_mutation(original)
            if not applied:
                continue
            mutated, kind = applied
            path.write_text(mutated, encoding="utf-8")
            syntax_ok = True
            try:
                compile(mutated, rel, "exec")
            except SyntaxError:
                syntax_ok = False

            present = mutated != original and kind in BEHAVIORAL_KINDS
            run = _run_suite(wt, harness["command"], timeout=420)

            outcome = classify_mutation_outcome(
                baseline_pass=baseline.get("passed"),
                mutated_pass=run.get("passed") if run.get("executed") else None,
                full_run_executed=bool(run.get("executed")),
                collection_only=False,
                behavioral=True,
                mutation_kind=kind,
                mutation_verified_present=present and syntax_ok,
                no_harness=False,
                blocked_env=bool(run.get("blocked")),
                invalid_sample=not syntax_ok,
            )
            if outcome == "MUTATION_KILLED":
                killed += 1
            elif outcome == "MUTATION_SURVIVED":
                survived += 1
            outcomes.append(outcome)

            rec = {
                "index": i + 1,
                "path": rel,
                "kind": kind,
                "syntax_ok_after_mutation": syntax_ok,
                "behavioral": True,
                "mutation_verified_present": present,
                "full_run_executed": bool(run.get("executed")),
                "collection_only": False,
                "baseline_passed": baseline.get("passed"),
                "mutated_passed": run.get("passed") if run.get("executed") else None,
                "test_reaction": outcome,
                "mutation_outcome": outcome,
            }
            out["mutations"].append(rec)
            out["provenance"]["mutated_runs"].append(
                {
                    "path": rel,
                    "kind": kind,
                    "returncode": run.get("returncode"),
                    "passed": run.get("passed"),
                    "outcome": outcome,
                }
            )
            path.write_text(original, encoding="utf-8")

            if killed >= 1 and i >= 1:
                break

        if not out["mutations"]:
            out["status"] = "NO_MUTATION_TARGETS"
            out["mutation_outcome"] = "INVALID_MUTATION_SAMPLE"
            out["dimension"] = "NOT_APPLICABLE"
            return out

        if "MUTATION_SURVIVED" in outcomes:
            agg = "MUTATION_SURVIVED"
        elif "MUTATION_KILLED" in outcomes:
            agg = "MUTATION_KILLED"
        elif "BLOCKED_ENVIRONMENT" in outcomes:
            agg = "BLOCKED_ENVIRONMENT"
        elif "MUTATION_VALIDATION_INCOMPLETE" in outcomes:
            agg = "MUTATION_VALIDATION_INCOMPLETE"
        elif "NO_RELEVANT_TEST_HARNESS_FOUND" in outcomes:
            agg = "NO_RELEVANT_TEST_HARNESS_FOUND"
        elif "NO_EXECUTABLE_TEST_COVERAGE" in outcomes:
            agg = "NO_EXECUTABLE_TEST_COVERAGE"
        else:
            agg = outcomes[0] if outcomes else "AUDIT_INCONCLUSIVE"

        if baseline.get("passed") is False:
            agg = "MUTATION_VALIDATION_INCOMPLETE"

        out["status"] = "SAMPLED"
        out["mutation_outcome"] = agg
        out["detected_count"] = killed
        out["survived_count"] = survived

        if agg == "MUTATION_KILLED" and killed >= 1:
            out["dimension"] = "ADEQUATE"
        elif agg == "MUTATION_SURVIVED":
            out["dimension"] = "CRITICAL"
        elif agg in {"NO_RELEVANT_TEST_HARNESS_FOUND", "NO_EXECUTABLE_TEST_COVERAGE"}:
            out["dimension"] = "NEEDS_WORK"
        elif agg in {"MUTATION_VALIDATION_INCOMPLETE", "AUDIT_INCONCLUSIVE", "MUTATION_TEST_NOT_EXECUTED"}:
            out["dimension"] = "NEEDS_WORK"
        elif agg == "BLOCKED_ENVIRONMENT":
            out["dimension"] = "BLOCKED"
        else:
            out["dimension"] = "NEEDS_WORK"

        return out
    except Exception as e:
        out["status"] = "ERROR"
        out["error"] = str(e)[:400]
        out["mutation_outcome"] = "AUDIT_INCONCLUSIVE"
        out["dimension"] = "BLOCKED"
        return out
    finally:
        try:
            subprocess.run(["git", "worktree", "prune"], cwd=str(root), capture_output=True, timeout=60)
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


def r5_finding_from_mutation(name: str, mut: dict[str, Any]) -> dict[str, Any] | None:
    """Map mutation outcome to R5 finding. S1 MUTATION_BLINDNESS only for proven survival.
    CRITICAL_TEST_COVERAGE_GAP S1 only when active first-party + material + no harness + concrete risk;
    else S2. BLOCKED_ENVIRONMENT alone ≠ S1.
    """
    outcome = mut.get("mutation_outcome")
    if outcome == "MUTATION_SURVIVED":
        # Verify survival evidence
        ok = False
        for m in mut.get("mutations") or []:
            if (
                m.get("mutation_outcome") == "MUTATION_SURVIVED"
                and m.get("behavioral")
                and m.get("full_run_executed")
                and m.get("baseline_passed") is True
                and m.get("mutated_passed") is True
                and m.get("kind") != "append_marker"
            ):
                ok = True
                break
        if not ok:
            return None
        return {
            "family": "R5",
            "severity": "S1",
            "repository": name,
            "kind": "MUTATION_BLINDNESS",
            "title": "Proven mutation survival: behavioral mutation not detected by full relevant suite",
            "detail": mut.get("mutations", [])[:3],
            "mutation_outcome": "MUTATION_SURVIVED",
            "disposition": "ROOT_CAUSE_S1",
            "reachability": {
                "reachability_status": "ACTIVE_FIRST_PARTY",
                "active": True,
                "first_party": True,
                "path_bucket": "PRODUCTION",
            },
            "requirement_capability_link": True,
            "semantic_review_disposition": "CONFIRMED_S1",
            "material_weakness": "mutation_survival",
        }

    # Incomplete / coverage / blocked findings only for R5 focus (avoid ecosystem inflation)
    if name not in R5_FOCUS:
        return None

    if outcome in {"NO_RELEVANT_TEST_HARNESS_FOUND", "NO_EXECUTABLE_TEST_COVERAGE"}:
        # Portal-like: material capability surface without executable harness → S2 unless
        # we have concrete active first-party risk signal (deep focus + no harness).
        concrete_risk = name in R5_FOCUS and outcome == "NO_RELEVANT_TEST_HARNESS_FOUND"
        # User: S1 CRITICAL_TEST_COVERAGE_GAP only if active first-party + material capability
        # + no meaningful harness + concrete risk (else S2).
        # We treat R5 focus without harness as S2 by default (coverage gap without proven
        # survival is not blindness); elevate to S1 only when there is production code AND
        # zero executable harness AND named material capability path — portal qualifies as S2
        # unless we assert concrete falsification risk. Prefer S2 honesty.
        sev = "S2"
        kind = "CRITICAL_TEST_COVERAGE_GAP" if sev == "S1" else "TEST_COVERAGE_GAP"
        if concrete_risk and False:  # reserved: do not force S1 without stronger evidence
            sev = "S1"
            kind = "CRITICAL_TEST_COVERAGE_GAP"
        return {
            "family": "R5",
            "severity": sev,
            "repository": name,
            "kind": kind,
            "title": f"No meaningful executable mutation harness ({outcome})",
            "detail": mut.get("mutations", [])[:3],
            "mutation_outcome": outcome,
            "disposition": "ROOT_CAUSE_S1" if sev == "S1" else "COVERAGE_GAP_S2",
            "reachability": {
                "reachability_status": "ACTIVE_FIRST_PARTY",
                "active": True,
                "first_party": True,
                "path_bucket": "PRODUCTION",
            },
            "material_weakness": "test_coverage_gap",
        }

    if outcome == "BLOCKED_ENVIRONMENT":
        return {
            "family": "R5",
            "severity": "S2",
            "repository": name,
            "kind": "mutation_blocked_environment",
            "title": "Mutation validation blocked by environment (not S1)",
            "mutation_outcome": outcome,
            "disposition": "BLOCKED_ENVIRONMENT",
        }

    if outcome in {
        "MUTATION_TEST_NOT_EXECUTED",
        "MUTATION_VALIDATION_INCOMPLETE",
        "AUDIT_INCONCLUSIVE",
        "INVALID_MUTATION_SAMPLE",
    }:
        return {
            "family": "R5",
            "severity": "S2",
            "repository": name,
            "kind": "mutation_evidence_incomplete",
            "title": f"Mutation evidence incomplete: {outcome}",
            "detail": mut.get("mutations", [])[:3],
            "mutation_outcome": outcome,
            "disposition": "INCOMPLETE_EVIDENCE",
        }

    # MUTATION_KILLED → no finding (adequate resistance)
    return None
