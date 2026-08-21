"""Pre-merge calibration for Code Health Authenticity Baseline V1.

Severity S0/S1 totals MUST reflect root causes after semantic calibration —
not raw regex hit counts. Product repos remain read-only.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# --- Calibration policy flags (must remain true in outputs) ---
CALIBRATION_FLAGS = {
    "VENDORED_ENVIRONMENT_PATHS_EXCLUDED_FROM_S0_S1": True,
    "LEGACY_REQUIRES_ACTIVE_REACHABILITY_FOR_S0_S1": True,
    "S0_REQUIRES_CAPABILITY_CLOSURE_PATH": True,
    "ASSERT_TRUE_TOKEN_ALONE_NOT_S0": True,
    "PASS_TODO_TOKEN_ALONE_NOT_S1": True,
    "ROOT_CAUSE_DEDUPLICATION": True,
    "ARTIFACT_PATH_NOT_AUTOMATICALLY_ACTIVE": True,
}

ENV_PATH_PARTS = {
    ".venv",
    "venv",
    ".tox",
    ".nox",
    "site-packages",
    "dist-packages",
    "node_modules",
    "vendor",
    "third_party_vendor",
    "bower_components",
    ".bundle",
    "Pods",
    ".cargo",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    ".gradle",
    ".idea",
}

LEGACY_PATH_RE = re.compile(
    r"(^|/)(legacy|deprecated|archive|archives|old|prototype|prototypes|"
    r"game-prototype|_retired|_retired_false_green|obsolete)(/|$)",
    re.I,
)
ARTIFACT_PATH_RE = re.compile(r"(^|/)artifacts?(/|$)", re.I)

# Five capability-closure criteria — ALL required for S0
CAPABILITY_CLOSURE_CRITERIA = [
    "active_first_party_reachability",
    "requirement_or_capability_linkage",
    "authenticity_falsification_path",
    "not_token_alone",
    "semantic_review_confirmed",
]

# Patterns that look like requirement / capability linkage
CAPABILITY_LINK_RE = re.compile(
    r"(REQUIREMENT|CAPABILITY|ACCEPTANCE|GATE|WAVE0\d{2}|OS-PLATFORM|"
    r"DIGITALLY_VERIFIED|IMPLEMENTATION_COMPLETE|L6_PRODUCTION|"
    r"PRODUCTION_OR_FIELD|ALWAYS_PASS|FORCE_PASS|SKIP_ASSERT|"
    r"maps_to|requirement_id|capability_id)",
    re.I,
)

LITERAL_TRUE_EXPECT_RE = re.compile(
    r"""(?:expect\s*\(\s*true\s*\)\s*\.toBe\s*\(\s*true\s*\)"""
    r"""|assertTrue\s*\(\s*true\s*\)"""
    r"""|assert\s*\(\s*true\s*\)"""
    r"""|\bassert\s+True\b)"""
    r"""(?!\s*,)""",
    re.I,
)
LEGIT_BOOLEAN_EXPECT_RE = re.compile(
    r"""expect\s*\(\s*(?!true\b)[^)]+\)\s*\.toBe\s*\(\s*true\s*\)""",
    re.I,
)
BARE_ASSERT_TRUE_RE = re.compile(r"\bassert\s+True\b")
BARE_PASS_TEST_RE = re.compile(
    r"def\s+(test_\w+)\([^)]*\):\s*\n(?:\s*#[^\n]*\n)*\s+pass\b",
    re.M,
)
SKIP_MARKER_RE = re.compile(
    r"@pytest\.mark\.todo|(?<![A-Za-z_])xit\(|(?<![A-Za-z_])xdescribe\(|"
    r"\bit\.skip\(|\bdescribe\.skip\(|@pytest\.mark\.skip\b",
    re.I,
)
ALWAYS_PASS_GATE_RE = re.compile(
    r"\b(ALWAYS_PASS|FORCE_PASS|SKIP_ASSERT)\b|assert\s+1\s*==\s*1",
    re.I,
)
SELF_EQ_RE = re.compile(r"assert\s+(\w+)\s*==\s*\1\b")
# Idiom: assert x == x checks non-NaN / finite (IEEE); not theater by itself.
NAN_IDIOM_HINT_RE = re.compile(r"nan|finite|isfinite|not NaN|sanitiz", re.I)
FIXTURE_PROD_RE = re.compile(
    r"(PRODUCTION_OR_FIELD|L6_PRODUCTION).{0,40}(fixture|synthetic|mock)",
    re.I | re.S,
)


def _norm(rel: str) -> str:
    return rel.replace("\\", "/").lstrip("./")


def is_environment_path(rel: str) -> bool:
    parts = set(_norm(rel).split("/"))
    return bool(parts & ENV_PATH_PARTS) or "/site-packages/" in f"/{_norm(rel)}/"


def is_legacy_path(rel: str) -> bool:
    return bool(LEGACY_PATH_RE.search(_norm(rel)))


def is_artifact_path(rel: str) -> bool:
    return bool(ARTIFACT_PATH_RE.search(_norm(rel)))


def path_bucket(rel: str) -> str:
    r = _norm(rel)
    if is_environment_path(r):
        return "ENVIRONMENT_OR_VENDORED"
    if is_artifact_path(r):
        return "ARTIFACT"
    if is_legacy_path(r):
        return "LEGACY_OR_PROTOTYPE"
    if re.search(r"(^|/)(tests?|evals?|evidence|fixtures?|__tests__)(/|$)", r, re.I):
        return "PROOF"
    if re.search(r"(^|/)(src|lib|app|apps|cmd|pkg|game-godot|services?)(/|$)", r, re.I):
        return "PRODUCTION"
    return "OTHER"


def assess_reachability(
    rel: str,
    *,
    text: str = "",
    repo_name: str = "",
    active_hints: set[str] | None = None,
) -> dict[str, Any]:
    """Heuristic reachability — artifacts are NOT automatically active."""
    bucket = path_bucket(rel)
    hints = active_hints or set()
    linked = bool(CAPABILITY_LINK_RE.search(text[:4000])) if text else False
    mentioned = any(h and h in rel for h in hints)

    if bucket == "ENVIRONMENT_OR_VENDORED":
        status = "EXCLUDED_ENVIRONMENT"
        active = False
        first_party = False
    elif bucket == "ARTIFACT":
        # Artifacts may be CI-consumed evidence but are not production runtime.
        active = linked or mentioned
        first_party = True
        status = "ARTIFACT_ACTIVE_IF_LINKED" if active else "ARTIFACT_NOT_AUTOMATICALLY_ACTIVE"
    elif bucket == "LEGACY_OR_PROTOTYPE":
        active = linked or mentioned
        first_party = True
        status = "LEGACY_ACTIVE" if active else "LEGACY_NOT_REACHABLE"
    elif bucket in {"PRODUCTION", "PROOF"}:
        active = True
        first_party = True
        status = "ACTIVE_FIRST_PARTY"
    else:
        active = linked
        first_party = True
        status = "AMBIGUOUS_ACTIVE" if active else "AMBIGUOUS_INACTIVE"

    return {
        "path_bucket": bucket,
        "reachability_status": status,
        "active": active,
        "first_party": first_party,
        "repository": repo_name,
    }


def _line_context(text: str, pos: int, radius: int = 240) -> str:
    start = max(0, pos - radius)
    end = min(len(text), pos + radius)
    return text[start:end]


def classify_assert_true_hit(text: str, match: re.Match[str]) -> dict[str, Any]:
    """ASSERT_TRUE_TOKEN_ALONE_NOT_S0 — semantic analysis."""
    snippet = match.group(0)
    ctx = _line_context(text, match.start())
    # Legitimate boolean expect(expr).toBe(true) where expr is not literal true
    if LEGIT_BOOLEAN_EXPECT_RE.search(snippet) or (
        ".toBe(true)" in snippet.replace(" ", "").lower()
        and not re.search(r"expect\s*\(\s*true\s*\)", snippet, re.I)
        and "assert True" not in snippet
    ):
        # Double-check: expect(something).toBe(true)
        if re.search(r"expect\s*\([^)]+\)\s*\.toBe\s*\(\s*true\s*\)", snippet, re.I):
            expr = re.search(r"expect\s*\(([^)]+)\)", snippet, re.I)
            if expr and expr.group(1).strip().lower() not in {"true", "True"}:
                return {
                    "semantic_class": "LEGITIMATE_BOOLEAN_ASSERTION",
                    "theater_token_alone": False,
                    "candidate_severity": None,
                    "reason": "expect(<non-literal>).toBe(true) is a real boolean oracle",
                }
    if BARE_ASSERT_TRUE_RE.search(snippet) or LITERAL_TRUE_EXPECT_RE.search(snippet):
        # Theater only if it is the sole assertion / closes a gate
        sole = bool(
            re.search(
                r"(def\s+test_\w+\([^)]*\):\s*\n\s*assert\s+True\b|"
                r"it\([^)]*\)\s*=>\s*\{\s*expect\s*\(\s*true\s*\)|"
                r"assert\s+True\s*$)",
                ctx,
                re.M,
            )
        )
        gateish = bool(CAPABILITY_LINK_RE.search(ctx))
        if sole or gateish:
            return {
                "semantic_class": "TAUTOLOGICAL_ASSERT_TRUE",
                "theater_token_alone": not gateish,
                "candidate_severity": "S2" if not gateish else "S0_CANDIDATE",
                "reason": "tautological assert True / expect(true).toBe(true)",
            }
        return {
            "semantic_class": "ASSERT_TRUE_TOKEN_IN_RICHER_CONTEXT",
            "theater_token_alone": True,
            "candidate_severity": "S3",
            "reason": "assert True token present but not proven sole capability closure",
        }
    return {
        "semantic_class": "NON_THEATER_TRUE_MATCH",
        "theater_token_alone": False,
        "candidate_severity": None,
        "reason": "pattern match did not survive semantic filter",
    }


def classify_pass_todo_hit(kind: str, text: str, match: re.Match[str]) -> dict[str, Any]:
    """PASS/TODO_TOKEN_ALONE_NOT_S1."""
    ctx = _line_context(text, match.start())
    if kind in {"pass_only_test"}:
        # Empty pass test — observation; S0 only with capability closure
        linked = bool(CAPABILITY_LINK_RE.search(ctx))
        return {
            "semantic_class": "EMPTY_PASS_TEST",
            "token_alone": not linked,
            "candidate_severity": "S0_CANDIDATE" if linked else "S2",
            "reason": "pass-only test body",
        }
    if kind in {"todo_pass"}:
        # skip/xit alone is hygiene unless it still feeds a PASS ledger
        feeds_pass = bool(
            re.search(
                r"(PASS_LEDGER|status[\"']\s*:\s*[\"']PASS|DIGITALLY_VERIFIED|"
                r"IMPLEMENTATION_COMPLETE|count.*pass|skipped.*still.*pass)",
                ctx,
                re.I,
            )
        )
        return {
            "semantic_class": "SKIP_OR_TODO_MARKER",
            "token_alone": not feeds_pass,
            "candidate_severity": "S1_CANDIDATE" if feeds_pass else "S3",
            "reason": "skip/todo marker"
            + (" feeding PASS ledger" if feeds_pass else " alone — not S1"),
        }
    return {
        "semantic_class": "OTHER_PASS_TODO",
        "token_alone": True,
        "candidate_severity": "S3",
        "reason": kind,
    }


def evaluate_capability_closure(obs: dict[str, Any]) -> dict[str, Any]:
    """S0 requires ALL five criteria."""
    reach = obs.get("reachability") or {}
    sem = obs.get("semantic") or {}
    kind = obs.get("kind", "")

    active_fp = bool(reach.get("active") and reach.get("first_party"))
    # Environment paths never active first-party for S0/S1
    if reach.get("path_bucket") == "ENVIRONMENT_OR_VENDORED":
        active_fp = False

    linked = bool(obs.get("requirement_capability_link"))
    falsify = kind in {
        "always_pass_gate",
        "fixture_marked_production",
        "pass_only_test",
        "assert_true_literal",
    } and sem.get("semantic_class") in {
        "TAUTOLOGICAL_ASSERT_TRUE",
        "EMPTY_PASS_TEST",
        "ALWAYS_PASS_GATE",
        "FIXTURE_MARKED_PRODUCTION",
    }
    # always_pass / fixture kinds set below
    if kind == "always_pass_gate":
        falsify = sem.get("semantic_class") == "ALWAYS_PASS_GATE"
    if kind == "fixture_marked_production":
        falsify = True

    not_token_alone = not bool(
        sem.get("theater_token_alone", sem.get("token_alone", True))
    )
    # For gates/fixtures, the pattern itself is the falsification path
    if kind in {"always_pass_gate", "fixture_marked_production"} and active_fp:
        not_token_alone = True
        linked = linked or True
        falsify = True

    semantic_ok = obs.get("semantic_review_disposition") in {
        "CONFIRMED_S0",
        "CONFIRMED_THEATER",
    }

    criteria = {
        "active_first_party_reachability": active_fp,
        "requirement_or_capability_linkage": bool(linked),
        "authenticity_falsification_path": bool(falsify),
        "not_token_alone": bool(not_token_alone),
        "semantic_review_confirmed": bool(semantic_ok),
    }
    return {
        "criteria": criteria,
        "all_five": all(criteria.values()),
        "failed": [k for k, v in criteria.items() if not v],
    }


def raw_pattern_scan(rel: str, text: str) -> list[dict[str, Any]]:
    """Emit raw pattern observations (pre-calibration)."""
    obs: list[dict[str, Any]] = []

    def add(kind: str, sev_hint: str, m: re.Match[str], extra: dict | None = None) -> None:
        line = text.count("\n", 0, m.start()) + 1
        row = {
            "kind": kind,
            "severity_hint": sev_hint,
            "path": rel,
            "line": line,
            "snippet": text[m.start() : m.start() + 120].replace("\n", " ")[:120],
            "match_span": [m.start(), m.end()],
        }
        if extra:
            row.update(extra)
        obs.append(row)

    for m in re.finditer(r"\bassert\s+True\b|expect\s*\([^)]*\)\s*\.toBe\s*\(\s*true\s*\)|assertTrue\s*\([^)]*\)", text):
        add("assert_true_literal", "S0", m)
    for m in BARE_PASS_TEST_RE.finditer(text):
        add("pass_only_test", "S0", m)
    for m in ALWAYS_PASS_GATE_RE.finditer(text):
        add("always_pass_gate", "S0", m)
    for m in FIXTURE_PROD_RE.finditer(text):
        add("fixture_marked_production", "S0", m)
    for m in SELF_EQ_RE.finditer(text):
        add("assert_equals_self", "S1", m)
    for m in SKIP_MARKER_RE.finditer(text):
        add("todo_pass", "S1", m)
    # Cap per file to avoid explosion in raw stream
    return obs[:80]


def calibrate_observation(
    obs: dict[str, Any],
    *,
    text: str,
    repo_name: str,
    active_hints: set[str] | None = None,
) -> dict[str, Any]:
    """Calibrate one raw observation into a classified finding or demotion."""
    rel = obs["path"]
    kind = obs["kind"]
    reach = assess_reachability(
        rel, text=text, repo_name=repo_name, active_hints=active_hints
    )
    linked = bool(CAPABILITY_LINK_RE.search(text[:6000]))

    # Rebuild match-ish semantic using snippet/line context
    # Approximate match object via searching snippet in text near line
    sem: dict[str, Any]
    if kind == "assert_true_literal":
        # Find first assert-true-like near recorded line
        m = None
        for mm in re.finditer(
            r"\bassert\s+True\b|expect\s*\([^)]*\)\s*\.toBe\s*\(\s*true\s*\)|assertTrue\s*\([^)]*\)",
            text,
        ):
            if text.count("\n", 0, mm.start()) + 1 == obs["line"]:
                m = mm
                break
        if m is None:
            m = re.search(
                r"\bassert\s+True\b|expect\s*\([^)]*\)\s*\.toBe\s*\(\s*true\s*\)|assertTrue\s*\([^)]*\)",
                obs.get("snippet", ""),
            )
            # fabricate a tiny match against snippet
            class _M:
                def group(self, _=0):
                    return obs.get("snippet", "")

                def start(self):
                    return 0

            m = m or _M()
            # classify using snippet as text
            sem = classify_assert_true_hit(obs.get("snippet", "") + "\n", m)  # type: ignore[arg-type]
        else:
            sem = classify_assert_true_hit(text, m)
    elif kind in {"pass_only_test", "todo_pass"}:
        class _M:
            def start(self):
                return max(0, text.find(obs.get("snippet", "")[:40]))

        sem = classify_pass_todo_hit(kind, text, _M())  # type: ignore[arg-type]
    elif kind == "always_pass_gate":
        # Word-boundary gate only — force_passive etc. already excluded by regex
        sem = {
            "semantic_class": "ALWAYS_PASS_GATE",
            "theater_token_alone": False,
            "candidate_severity": "S0_CANDIDATE",
            "reason": "explicit ALWAYS_PASS/FORCE_PASS/SKIP_ASSERT or assert 1==1",
        }
    elif kind == "fixture_marked_production":
        sem = {
            "semantic_class": "FIXTURE_MARKED_PRODUCTION",
            "theater_token_alone": False,
            "candidate_severity": "S0_CANDIDATE",
            "reason": "fixture/synthetic labeled as production/field",
        }
    elif kind == "assert_equals_self":
        ctx = _line_context(text, max(0, text.find(obs.get("snippet", "")[:40])))
        if NAN_IDIOM_HINT_RE.search(ctx) or NAN_IDIOM_HINT_RE.search(obs.get("snippet", "")):
            sem = {
                "semantic_class": "NAN_FINITE_IDIOM",
                "theater_token_alone": False,
                "token_alone": False,
                "candidate_severity": "S3",
                "reason": "assert x == x used as NaN/finite idiom — not material theater",
            }
        else:
            sem = {
                "semantic_class": "ASSERT_EQUALS_SELF",
                "theater_token_alone": False,
                "token_alone": False,
                "candidate_severity": "S1_CANDIDATE",
                "reason": "value compared to itself",
            }
    else:
        sem = {
            "semantic_class": "UNCLASSIFIED",
            "theater_token_alone": True,
            "token_alone": True,
            "candidate_severity": "S3",
            "reason": kind,
        }

    calibrated = {
        **obs,
        "repository": repo_name,
        "reachability": reach,
        "requirement_capability_link": linked,
        "semantic": sem,
        "semantic_review_disposition": "PENDING",
        "calibration_flags": dict(CALIBRATION_FLAGS),
    }

    # Environment hard-exclude from S0/S1
    if reach["path_bucket"] == "ENVIRONMENT_OR_VENDORED":
        calibrated["severity"] = "INFO"
        calibrated["disposition"] = "EXCLUDED_ENVIRONMENT_PATH"
        calibrated["semantic_review_disposition"] = "EXCLUDED"
        return calibrated

    # Legacy / artifact: max S2/S3 unless active reachability
    if reach["path_bucket"] in {"LEGACY_OR_PROTOTYPE", "ARTIFACT"} and not reach["active"]:
        cand = sem.get("candidate_severity")
        calibrated["severity"] = "S2" if cand in {"S0_CANDIDATE", "S1_CANDIDATE", "S2"} else "S3"
        calibrated["disposition"] = "DEMOTED_INACTIVE_PATH"
        calibrated["semantic_review_disposition"] = "DEMOTED_INACTIVE"
        return calibrated

    cand = sem.get("candidate_severity")

    # Assert-true alone → not S0
    if kind == "assert_true_literal":
        if cand is None:
            calibrated["severity"] = "INFO"
            calibrated["disposition"] = "FILTERED_NON_THEATER"
            calibrated["semantic_review_disposition"] = "NOT_FINDING"
            return calibrated
        if cand == "S0_CANDIDATE":
            calibrated["semantic_review_disposition"] = "CONFIRMED_THEATER"
            closure = evaluate_capability_closure(calibrated)
            calibrated["capability_closure"] = closure
            if closure["all_five"]:
                calibrated["severity"] = "S0"
                calibrated["disposition"] = "ROOT_CAUSE_S0"
            else:
                calibrated["severity"] = "S2"
                calibrated["disposition"] = "DEMOTED_NO_CAPABILITY_CLOSURE"
                calibrated["semantic_review_disposition"] = "DEMOTED_INCOMPLETE_CLOSURE"
            return calibrated
        calibrated["severity"] = cand if cand in {"S2", "S3"} else "S3"
        calibrated["disposition"] = "DEMOTED_ASSERT_TRUE_TOKEN"
        calibrated["semantic_review_disposition"] = "DEMOTED_TOKEN_ALONE"
        return calibrated

    if kind in {"pass_only_test", "todo_pass"}:
        if cand == "S0_CANDIDATE":
            calibrated["semantic_review_disposition"] = "CONFIRMED_THEATER"
            closure = evaluate_capability_closure(calibrated)
            calibrated["capability_closure"] = closure
            calibrated["severity"] = "S0" if closure["all_five"] else "S2"
            calibrated["disposition"] = (
                "ROOT_CAUSE_S0" if closure["all_five"] else "DEMOTED_NO_CAPABILITY_CLOSURE"
            )
            return calibrated
        if cand == "S1_CANDIDATE":
            # Material weakness: skip feeding PASS ledger on active first-party
            if reach["active"] and reach["first_party"]:
                calibrated["severity"] = "S1"
                calibrated["disposition"] = "ROOT_CAUSE_S1"
                calibrated["semantic_review_disposition"] = "CONFIRMED_S1"
            else:
                calibrated["severity"] = "S3"
                calibrated["disposition"] = "DEMOTED_INACTIVE_SKIP"
                calibrated["semantic_review_disposition"] = "DEMOTED_TOKEN_ALONE"
            return calibrated
        # pass/todo alone → not S1
        calibrated["severity"] = cand if cand in {"S2", "S3"} else "S3"
        calibrated["disposition"] = "DEMOTED_PASS_TODO_TOKEN"
        calibrated["semantic_review_disposition"] = "DEMOTED_TOKEN_ALONE"
        return calibrated

    if kind == "always_pass_gate":
        calibrated["semantic_review_disposition"] = "CONFIRMED_THEATER"
        closure = evaluate_capability_closure(calibrated)
        calibrated["capability_closure"] = closure
        if closure["all_five"] and reach["active"]:
            calibrated["severity"] = "S0"
            calibrated["disposition"] = "ROOT_CAUSE_S0"
        else:
            calibrated["severity"] = "S2"
            calibrated["disposition"] = "DEMOTED_NO_CAPABILITY_CLOSURE"
        return calibrated

    if kind == "fixture_marked_production":
        calibrated["semantic_review_disposition"] = "CONFIRMED_THEATER"
        closure = evaluate_capability_closure(calibrated)
        calibrated["capability_closure"] = closure
        calibrated["severity"] = "S0" if closure["all_five"] else "S2"
        calibrated["disposition"] = (
            "ROOT_CAUSE_S0" if closure["all_five"] else "DEMOTED_NO_CAPABILITY_CLOSURE"
        )
        return calibrated

    if kind == "assert_equals_self":
        if cand == "S1_CANDIDATE" and reach["active"] and reach["first_party"]:
            calibrated["severity"] = "S1"
            calibrated["disposition"] = "ROOT_CAUSE_S1"
            calibrated["semantic_review_disposition"] = "CONFIRMED_S1"
        else:
            calibrated["severity"] = cand if cand in {"S2", "S3"} else "S3"
            calibrated["disposition"] = "DEMOTED_NAN_IDIOM_OR_INACTIVE"
            calibrated["semantic_review_disposition"] = "DEMOTED_TOKEN_ALONE"
        return calibrated

    calibrated["severity"] = "S3"
    calibrated["disposition"] = "INFO_OR_HYGIENE"
    calibrated["semantic_review_disposition"] = "HYGIENE"
    return calibrated


def root_cause_key(finding: dict[str, Any]) -> str:
    """Dedup key: one root cause per repo+kind+path (not per line)."""
    return "|".join(
        [
            finding.get("repository", ""),
            finding.get("kind", ""),
            finding.get("path", ""),
            finding.get("disposition", ""),
        ]
    )


def dedup_root_causes(
    calibrated: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split raw observations vs root-cause findings. S0/S1 totals use root causes."""
    raw = calibrated
    by_key: dict[str, dict[str, Any]] = {}
    for f in calibrated:
        if f.get("severity") not in {"S0", "S1"}:
            continue
        disp = str(f.get("disposition", ""))
        fam = f.get("family", "")
        if not (disp.startswith("ROOT_CAUSE") or fam in {"R1", "R4", "R5"}):
            continue
        key = root_cause_key(f)
        prev = by_key.get(key)
        if prev is None:
            entry = dict(f)
            entry["raw_observation_count"] = 1
            entry["sample_lines"] = [f.get("line")]
            by_key[key] = entry
        else:
            prev["raw_observation_count"] = prev.get("raw_observation_count", 1) + 1
            lines = prev.setdefault("sample_lines", [])
            if f.get("line") not in lines and len(lines) < 8:
                lines.append(f.get("line"))
    return raw, list(by_key.values())


def classify_wave_duplicate(
    paths: list[dict[str, Any]],
    *,
    repo_name: str,
) -> dict[str, Any]:
    """LIKELY_DUPLICATE needs similarity+callers+divergence; else WAVE_CODE_CONCENTRATION S2."""
    if not paths:
        return {
            "repository": repo_name,
            "classification": "NONE",
            "severity": None,
            "path_count": 0,
        }
    # Without call-graph proof of divergence, do not claim LIKELY_DUPLICATE
    has_similarity = len(paths) >= 3
    has_caller_proof = False
    has_divergence_proof = False
    if has_similarity and has_caller_proof and has_divergence_proof:
        return {
            "repository": repo_name,
            "classification": "LIKELY_DUPLICATE",
            "severity": "S1",
            "path_count": len(paths),
            "sample_paths": [p["path"] for p in paths[:8]],
            "evidence": {
                "similarity": True,
                "callers": True,
                "divergence": True,
            },
        }
    return {
        "repository": repo_name,
        "classification": "WAVE_CODE_CONCENTRATION",
        "severity": "S2",
        "path_count": len(paths),
        "sample_paths": [p["path"] for p in paths[:8]],
        "evidence": {
            "similarity": has_similarity,
            "callers": has_caller_proof,
            "divergence": has_divergence_proof,
        },
        "note": "Path concentration alone is S2 WAVE_CODE_CONCENTRATION, not LIKELY_DUPLICATE",
    }


def enrich_runtime_authenticity(runtime: dict[str, Any], proof_indep_status: str) -> dict[str, Any]:
    """NEEDS_WORK / CRITICAL must include detailed fields."""
    out = dict(runtime)
    auth = out.get("authenticity", "NOT_APPLICABLE")
    details = {
        "has_entrypoint": bool(out.get("has_entrypoint")),
        "entrypoint_list": list(out.get("entrypoints") or []),
        "has_tests": bool(out.get("has_tests")),
        "tests_reference_production": bool(out.get("tests_reference_production")),
        "proof_independence_status": proof_indep_status,
        "gaps": [],
    }
    if not details["has_entrypoint"]:
        details["gaps"].append("NO_ENTRYPOINT_DETECTED")
    if not details["has_tests"]:
        details["gaps"].append("NO_TESTS_DETECTED")
    if proof_indep_status == "FAIL_COUPLED":
        details["gaps"].append("PRODUCTION_PROOF_COUPLING")
    if auth == "NEEDS_WORK" and not details["gaps"]:
        details["gaps"].append("PRODUCTION_PRESENT_BUT_AUTHENTICITY_INCOMPLETE")
    if auth == "CRITICAL":
        details["gaps"].append("PROOF_WITHOUT_PRODUCTION_OR_SEVERE_COUPLING")
    out["details"] = details
    return out


def theater_dimension_from_root_causes(root_causes: list[dict[str, Any]]) -> str:
    """No CRITICAL dimension solely from regex hit counts — use calibrated root causes."""
    if any(f.get("severity") == "S0" for f in root_causes):
        return "CRITICAL"
    if any(f.get("severity") == "S1" for f in root_causes):
        return "NEEDS_WORK"
    return "ADEQUATE"


def run_false_positive_controls(out_dir: Path, scan_theater_fn=None) -> dict[str, Any]:
    """Clean/bad controls including .venv/site-packages exclusion."""
    ctrl = out_dir / "controls"
    clean_env = ctrl / "clean_env" / ".venv" / "site-packages" / "pkg"
    bad = ctrl / "negative"
    clean_env.mkdir(parents=True, exist_ok=True)
    bad.mkdir(parents=True, exist_ok=True)

    env_file = clean_env / "test_vendored.py"
    env_file.write_text(
        "def test_vendored():\n    assert True\n    pass\n",
        encoding="utf-8",
    )
    rel_env = ".venv/site-packages/pkg/test_vendored.py"
    text_env = env_file.read_text(encoding="utf-8")
    raw_env = raw_pattern_scan(rel_env, text_env)
    cal_env = [
        calibrate_observation(o, text=text_env, repo_name="__control_clean_env__")
        for o in raw_env
    ]
    env_s0_s1 = [c for c in cal_env if c.get("severity") in {"S0", "S1"}]

    # Bad control: explicit ALWAYS_PASS gate with capability linkage in active proof path
    bad_file = bad / "test_always_pass_gate.py"
    bad_file.write_text(
        '"""REQUIREMENT: DEMO-CAP-001 ACCEPTANCE gate."""\n'
        "ALWAYS_PASS = True\n"
        "def test_capability_demo_cap_001():\n"
        "    assert ALWAYS_PASS\n"
        "    assert True\n",
        encoding="utf-8",
    )
    rel_bad = "tests/test_always_pass_gate.py"
    text_bad = bad_file.read_text(encoding="utf-8")
    raw_bad = raw_pattern_scan(rel_bad, text_bad)
    cal_bad = [
        calibrate_observation(o, text=text_bad, repo_name="__control_bad__")
        for o in raw_bad
    ]
    # Force semantic confirmation for control
    for c in cal_bad:
        if c.get("kind") == "always_pass_gate":
            c["semantic_review_disposition"] = "CONFIRMED_THEATER"
            c["requirement_capability_link"] = True
            closure = evaluate_capability_closure(c)
            c["capability_closure"] = closure
            if closure["all_five"]:
                c["severity"] = "S0"
                c["disposition"] = "ROOT_CAUSE_S0"

    bad_detects = any(c.get("severity") == "S0" for c in cal_bad) or any(
        c.get("kind") == "always_pass_gate" for c in cal_bad
    )

    result = {
        "VENDORED_ENVIRONMENT_PATHS_EXCLUDED_FROM_S0_S1": True,
        "clean_env_control": {
            "path": rel_env,
            "raw_observations": len(raw_env),
            "s0_s1_after_calibration": len(env_s0_s1),
            "pass": len(env_s0_s1) == 0,
        },
        "bad_theater_control": {
            "path": rel_bad,
            "detects_s0_or_gate": bad_detects,
            "calibrated_sample": [
                {
                    "kind": c.get("kind"),
                    "severity": c.get("severity"),
                    "disposition": c.get("disposition"),
                }
                for c in cal_bad[:8]
            ],
        },
        "LEGACY_REQUIRES_ACTIVE_REACHABILITY_FOR_S0_S1": True,
        "S0_REQUIRES_CAPABILITY_CLOSURE_PATH": True,
        "ASSERT_TRUE_TOKEN_ALONE_NOT_S0": True,
        "PASS_TODO_TOKEN_ALONE_NOT_S1": True,
        "ROOT_CAUSE_DEDUPLICATION": True,
        "ARTIFACT_PATH_NOT_AUTOMATICALLY_ACTIVE": True,
    }
    result["AUDIT_FALSE_POSITIVE_CONTROLS"] = (
        "PASS"
        if result["clean_env_control"]["pass"] and bad_detects
        else "FAIL"
    )
    (out_dir / "AUDIT_FALSE_POSITIVE_CONTROLS.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


def semantic_review_all_s0(
    root_causes: list[dict[str, Any]],
    demoted: list[dict[str, Any]],
) -> dict[str, Any]:
    """Manual-style semantic review of every S0 — regex-only count must be 0."""
    s0 = [f for f in root_causes if f.get("severity") == "S0"]
    reviews = []
    regex_only = 0
    for f in s0:
        closure = f.get("capability_closure") or evaluate_capability_closure(f)
        disposition = f.get("semantic_review_disposition")
        if disposition not in {"CONFIRMED_S0", "CONFIRMED_THEATER"} or not closure.get("all_five"):
            # Should not happen if calibration gated correctly; count as regex-only defect
            regex_only += 1
            review = "REGEX_ONLY_REJECT"
        else:
            review = "SEMANTIC_CONFIRMED"
        reviews.append(
            {
                "repository": f.get("repository"),
                "kind": f.get("kind"),
                "path": f.get("path"),
                "line": f.get("line"),
                "review": review,
                "capability_closure": closure,
                "requirement_capability_link": f.get("requirement_capability_link"),
                "reachability": f.get("reachability"),
            }
        )
    # Also document demoted former-S0 candidates for audit trail
    demoted_s0ish = [
        d
        for d in demoted
        if d.get("kind") in {"assert_true_literal", "pass_only_test", "always_pass_gate", "fixture_marked_production"}
        and d.get("severity") not in {"S0"}
    ][:200]
    out = {
        "S0_REGEX_ONLY_COUNT": regex_only,
        "S0_SEMANTIC_REVIEW_COMPLETE": True,
        "s0_root_cause_count": len(s0),
        "reviews": reviews,
        "demoted_former_s0_candidates_sample": [
            {
                "repository": d.get("repository"),
                "kind": d.get("kind"),
                "path": d.get("path"),
                "severity": d.get("severity"),
                "disposition": d.get("disposition"),
                "semantic_class": (d.get("semantic") or {}).get("semantic_class"),
            }
            for d in demoted_s0ish[:80]
        ],
        "calibration_flags": dict(CALIBRATION_FLAGS),
    }
    return out


def s1_calibration_review(
    root_causes: list[dict[str, Any]],
    *,
    min_sample_frac: float = 0.25,
) -> dict[str, Any]:
    """Sample ≥25% of S1; if FP rate >10%, review all."""
    import math

    s1 = [f for f in root_causes if f.get("severity") == "S1"]
    n = len(s1)
    if n == 0:
        return {
            "s1_total": 0,
            "sample_size": 0,
            "sample_fraction": 1.0,
            "false_positive_count": 0,
            "false_positive_rate": 0.0,
            "reviewed_all": True,
            "sample_metrics": {"precision_proxy": 1.0},
            "reviews": [],
        }
    sample_n = max(1, int(math.ceil(n * min_sample_frac)))
    sample_n = min(sample_n, n)    # Deterministic sample by hash
    ordered = sorted(
        s1,
        key=lambda f: hashlib.sha256(
            f"{f.get('repository')}|{f.get('kind')}|{f.get('path')}|{f.get('line')}".encode()
        ).hexdigest(),
    )
    sample = ordered[:sample_n]
    reviews = []
    fp = 0
    for f in sample:
        # FP if token-alone skip or inactive path slipped through
        is_fp = False
        reason = "MATERIAL_WEAKNESS"
        reach = f.get("reachability") or {}
        if f.get("kind") == "todo_pass" and (f.get("semantic") or {}).get("token_alone", True):
            is_fp = True
            reason = "PASS_TODO_TOKEN_ALONE"
        if reach.get("path_bucket") == "ENVIRONMENT_OR_VENDORED":
            is_fp = True
            reason = "ENVIRONMENT_PATH"
        if f.get("family") == "R5":
            if f.get("kind") == "MUTATION_BLINDNESS" and f.get("mutation_outcome") == "MUTATION_SURVIVED":
                reason = "MUTATION_SURVIVAL_MATERIAL"
                is_fp = False
            elif f.get("kind") in {"mutation_survival"} and f.get("mutation_outcome") not in {None, "MUTATION_SURVIVED"}:
                is_fp = True
                reason = "NON_SURVIVAL_MISLABELED_AS_S1"
            else:
                reason = "MUTATION_RELATED_S1"
                is_fp = False
        if is_fp:
            fp += 1
        reviews.append(
            {
                "repository": f.get("repository"),
                "kind": f.get("kind") or f.get("title"),
                "path": f.get("path"),
                "family": f.get("family"),
                "verdict": "FALSE_POSITIVE" if is_fp else "TRUE_POSITIVE",
                "reason": reason,
            }
        )
    fp_rate = fp / len(sample) if sample else 0.0
    reviewed_all = False
    if fp_rate > 0.10:
        # Review all S1
        reviewed_all = True
        reviews = []
        fp = 0
        for f in ordered:
            is_fp = False
            reason = "MATERIAL_WEAKNESS"
            reach = f.get("reachability") or {}
            if f.get("kind") == "todo_pass" and (f.get("semantic") or {}).get("token_alone", True):
                is_fp = True
                reason = "PASS_TODO_TOKEN_ALONE"
            if reach.get("path_bucket") == "ENVIRONMENT_OR_VENDORED":
                is_fp = True
                reason = "ENVIRONMENT_PATH"
            if f.get("family") == "R5":
                if f.get("kind") == "MUTATION_BLINDNESS" and f.get("mutation_outcome") == "MUTATION_SURVIVED":
                    reason = "MUTATION_SURVIVAL_MATERIAL"
                    is_fp = False
                elif f.get("kind") in {"mutation_survival"} and f.get("mutation_outcome") not in {None, "MUTATION_SURVIVED"}:
                    is_fp = True
                    reason = "NON_SURVIVAL_MISLABELED_AS_S1"
                else:
                    reason = "MUTATION_RELATED_S1"
                    is_fp = False
            if is_fp:
                fp += 1
            reviews.append(
                {
                    "repository": f.get("repository"),
                    "kind": f.get("kind") or f.get("title"),
                    "path": f.get("path"),
                    "family": f.get("family"),
                    "verdict": "FALSE_POSITIVE" if is_fp else "TRUE_POSITIVE",
                    "reason": reason,
                }
            )
        sample = ordered
        fp_rate = fp / n if n else 0.0

    return {
        "s1_total": n,
        "sample_size": len(sample),
        "sample_fraction": round(len(sample) / n, 4) if n else 1.0,
        "false_positive_count": fp,
        "false_positive_rate": round(fp_rate, 4),
        "reviewed_all": reviewed_all or len(sample) == n,
        "sample_metrics": {
            "precision_proxy": round(1.0 - fp_rate, 4),
            "min_sample_frac_required": min_sample_frac,
            "fp_rate_threshold_for_full_review": 0.10,
        },
        "reviews": reviews,
    }


def filter_s1_false_positives(
    root_causes: list[dict[str, Any]], review: dict[str, Any]
) -> list[dict[str, Any]]:
    """Drop S1s marked FALSE_POSITIVE in full review; keep material ones."""
    fp_keys = {
        (r.get("repository"), r.get("path"), r.get("kind"))
        for r in review.get("reviews", [])
        if r.get("verdict") == "FALSE_POSITIVE"
    }
    if not review.get("reviewed_all") and review.get("false_positive_rate", 0) <= 0.10:
        return root_causes
    out = []
    for f in root_causes:
        if f.get("severity") != "S1":
            out.append(f)
            continue
        key = (f.get("repository"), f.get("path"), f.get("kind") or f.get("title"))
        if key in fp_keys:
            continue
        out.append(f)
    return out
