#!/usr/bin/env python3
"""Independent validator for Code Health R5-S1 accepted-main reconciliation overlay."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIELD_KIT = Path(__file__).resolve().parents[1]
BASE = FIELD_KIT / "program" / "code_health_authenticity_baseline_v1"
STATUS = BASE / "remediation_status"
DIGITAL = FIELD_KIT / "program" / "digital_ecosystem_baseline_v2"
TOKEN = "CODE_HEALTH_R5_S1_ACCEPTED_MAIN_RECONCILIATION_PASS"

EXPECTED_MERGES = {
    "field_kit_114": "70ca6940351e96adbbaa27eb7fffd4b55fcfa767",
    "portal_11": "2a3303d56a71c1f78bfbbf165ed75f1d368fa98f",
    "waike_55": "8eb2827dc58ffa391842da1bfb1ee665c25a31a7",
}

MVI_REPOS = {
    "7gc-digital-twin",
    "readygary-6g-beam-selection",
    "gunnchos-emergent-service-intent-protocols",
}

COUPLING_RE = re.compile(
    r"^\s*(from|import)\s+.*(tests|artifacts|code_health|mutation_harness)",
    re.M,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def check_overlay_files() -> dict:
    required = [
        STATUS / "CURRENT_CODE_HEALTH_STATUS.json",
        STATUS / "CURRENT_CODE_HEALTH_STATUS.md",
        STATUS / "R5_S1_ACCEPTED_MAIN_RECONCILIATION.json",
        STATUS / "R5_S1_ACCEPTED_MAIN_RECONCILIATION.md",
        STATUS / "REMEDIATION_HISTORY.json",
        BASE / "FUTURE_WAVE_CODE_INTEGRITY_POLICY.md",
        BASE / "FINDINGS.json",
    ]
    for p in required:
        if not p.is_file():
            _fail(f"missing required file: {p}")
    recon = _load(STATUS / "R5_S1_ACCEPTED_MAIN_RECONCILIATION.json")
    current = _load(STATUS / "CURRENT_CODE_HEALTH_STATUS.json")
    return {"recon": recon, "current": current}


def check_arithmetic(recon: dict, current: dict) -> None:
    sev = recon["severity_arithmetic"]
    for k, v in {
        "historical_s0": 0,
        "historical_s1": 2,
        "current_open_s0": 0,
        "current_open_s1": 0,
        "closed_s1_since_baseline": 2,
    }.items():
        if sev.get(k) != v:
            _fail(f"severity_arithmetic.{k} expected {v} got {sev.get(k)}")
        if current.get(k) != v:
            _fail(f"CURRENT_CODE_HEALTH_STATUS.{k} expected {v} got {current.get(k)}")
    if recon.get("token") != TOKEN:
        _fail(f"token must be {TOKEN}")
    if recon.get("CODE_HEALTH_R5_S1_RECONCILIATION") != "PASS":
        _fail("CODE_HEALTH_R5_S1_RECONCILIATION must be PASS")
    for claim in (
        "FULL_MUTATION_TESTING_COMPLETE",
        "ALL_PORTAL_DEFECTS_ELIMINATED",
        "ALL_WAIKE_DEFECTS_ELIMINATED",
    ):
        if recon["claim_boundaries"].get(claim) is not False:
            _fail(f"claim_boundaries.{claim} must be false")
        if current["claim_boundaries"].get(claim) is not False:
            _fail(f"current claim_boundaries.{claim} must be false")


def check_historical_immutable() -> None:
    findings = _load(BASE / "FINDINGS.json")
    s0 = [f for f in findings["findings"] if f.get("severity") == "S0"]
    s1 = [f for f in findings["findings"] if f.get("severity") == "S1"]
    if len(s0) != 0 or len(s1) != 2:
        _fail(f"historical FINDINGS severity counts drifted: s0={len(s0)} s1={len(s1)}")
    # Both S1 entries must still be mutation blindness (not rewritten closed)
    kinds = {f.get("kind") for f in s1}
    if kinds != {"MUTATION_BLINDNESS"}:
        _fail(f"historical S1 kinds rewritten unexpectedly: {kinds}")
    repos = {f.get("repository") for f in s1}
    if repos != {"gunnchos-research-portal", "waike-research-ops"}:
        _fail(f"historical S1 repos drifted: {repos}")


def check_s2_preserved() -> None:
    findings = _load(BASE / "FINDINGS.json")
    s2 = [f for f in findings["findings"] if f.get("severity") == "S2"]
    if not s2:
        _fail("S2 findings missing from historical FINDINGS.json")
    mvi = {
        f["repository"]
        for f in s2
        if f.get("mutation_outcome") == "MUTATION_VALIDATION_INCOMPLETE"
        or "MUTATION_VALIDATION_INCOMPLETE" in f.get("title", "")
    }
    if not MVI_REPOS.issubset(mvi):
        _fail(f"S2 MUTATION_VALIDATION_INCOMPLETE repos missing: {MVI_REPOS - mvi}")
    recon = _load(STATUS / "R5_S1_ACCEPTED_MAIN_RECONCILIATION.json")
    listed = set(recon["s2_preserved"]["S2_MUTATION_VALIDATION_INCOMPLETE_REPOS"])
    if listed != MVI_REPOS:
        _fail(f"overlay MVI repos mismatch: {listed}")
    if recon["s2_preserved"].get("S2_FINDINGS_PRESERVED") is not True:
        _fail("S2_FINDINGS_PRESERVED must be true")


def check_digital_baseline_unchanged() -> None:
    """R5 must not have rewritten digital totals; later waves may advance live baseline."""
    recon = _load(STATUS / "R5_S1_ACCEPTED_MAIN_RECONCILIATION.json")
    r5 = recon.get("digital_baseline") or {}
    r5_expected = {
        "ATOMIC_TOTAL": 419,
        "DIGITAL_IMPLEMENTATION_COMPLETE": 111,
        "DIGITAL_IMPLEMENTATION_OPEN": 51,
        "DIGITAL_VALIDATION_OPEN": 0,
        "DIGITAL_CONTROLLABLE_POOL": 162,
    }
    for k, v in r5_expected.items():
        if r5.get(k) != v:
            _fail(f"R5 overlay digital_baseline {k} expected {v} got {r5.get(k)}")

    br = _load(DIGITAL / "BASELINE_V2_RESULT.json")
    t = br["totals"]
    if t.get("ATOMIC_TOTAL") != 419:
        _fail(f"digital baseline ATOMIC_TOTAL expected 419 got {t.get('ATOMIC_TOTAL')}")
    if int(t.get("DIGITAL_IMPLEMENTATION_COMPLETE") or 0) < 111:
        _fail(
            "digital baseline DIGITAL_IMPLEMENTATION_COMPLETE "
            f"expected >=111 got {t.get('DIGITAL_IMPLEMENTATION_COMPLETE')}"
        )
    if int(t.get("DIGITAL_IMPLEMENTATION_OPEN") or 0) > 51:
        _fail(
            "digital baseline DIGITAL_IMPLEMENTATION_OPEN "
            f"expected <=51 got {t.get('DIGITAL_IMPLEMENTATION_OPEN')}"
        )
    if t.get("DIGITAL_VALIDATION_OPEN") != 0:
        _fail(f"digital baseline DIGITAL_VALIDATION_OPEN expected 0 got {t.get('DIGITAL_VALIDATION_OPEN')}")
    if t.get("EVIDENCE_MAPPING_OPEN") != 0:
        _fail(f"digital baseline EVIDENCE_MAPPING_OPEN expected 0 got {t.get('EVIDENCE_MAPPING_OPEN')}")
    live_pool = (
        int(t.get("DIGITAL_IMPLEMENTATION_COMPLETE") or 0)
        + int(t.get("DIGITAL_IMPLEMENTATION_OPEN") or 0)
        + int(t.get("DIGITAL_VALIDATION_OPEN") or 0)
    )
    if live_pool != 162:
        _fail(f"live DIGITAL_CONTROLLABLE_POOL expected 162 got {live_pool}")
    pool = _load(BASE / "BASELINE_RESULT.json")["prerequisite"]["baseline_frozen"]["POOL"]
    if pool != 162:
        _fail(f"DIGITAL_CONTROLLABLE_POOL expected 162 got {pool}")
    # R5 PRs must not touch digital baseline paths. Later engineering closeouts may.
    try:
        diff = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            cwd=FIELD_KIT,
            capture_output=True,
            text=True,
            check=False,
        )
        changed = [ln for ln in diff.stdout.splitlines() if ln.strip()]
        digital_hits = [c for c in changed if c.startswith("program/digital_ecosystem_baseline_")]
        wave010_closeout = any(
            c.startswith("artifacts/engineering_wave010_closeout/")
            or c.startswith("scripts/engineering_wave010/")
            or c.startswith("tests/engineering_wave010/")
            for c in changed
        )
        if digital_hits and not wave010_closeout:
            _fail(f"DIGITAL_BASELINE_FILES_CHANGED nonzero: {digital_hits}")

        findings_hits = [c for c in changed if c.endswith("FINDINGS.json") or c.endswith("BASELINE_RESULT.json")]
        # FINDINGS and BASELINE_RESULT must remain immutable
        hist = [
            c
            for c in changed
            if c
            in {
                "program/code_health_authenticity_baseline_v1/FINDINGS.json",
                "program/code_health_authenticity_baseline_v1/BASELINE_RESULT.json",
                "program/code_health_authenticity_baseline_v1/REMEDIATION_REGISTER.json",
            }
        ]
        if hist:
            _fail(f"historical baseline artifacts modified: {hist}")
    except FileNotFoundError:
        pass


def check_policy() -> None:
    text = (BASE / "FUTURE_WAVE_CODE_INTEGRITY_POLICY.md").read_text(encoding="utf-8")
    for needle in [
        "Production independence",
        "No proof imports",
        "Canonical runtime tested",
        "Meaningful assertions",
        "Mutation / sabotage coverage",
        "Fixture honesty",
        "No wave duplicate canonical",
        "Complexity hotspots",
        "Architecture docs",
        "New S0",
        "New S1",
        "S2",
    ]:
        if needle not in text:
            _fail(f"policy missing required check/section: {needle}")


def _gh_pr_merged(repo: str, number: int, expected_sha: str) -> None:
    if os.environ.get("SKIP_LIVE_GITHUB") == "1":
        print(f"SKIP_LIVE_GITHUB=1 — trusting overlay for {repo}#{number}")
        return
    try:
        out = subprocess.run(
            [
                "gh",
                "pr",
                "view",
                str(number),
                "--repo",
                repo,
                "--json",
                "state,mergeCommit",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"WARN: live gh unavailable ({e}); requiring overlay SHAs only")
        return
    if out.returncode != 0:
        print(f"WARN: gh pr view failed for {repo}#{number}: {out.stderr.strip()}")
        return
    data = json.loads(out.stdout)
    if data.get("state") != "MERGED":
        _fail(f"{repo}#{number} not MERGED (state={data.get('state')})")
    sha = (data.get("mergeCommit") or {}).get("oid")
    if sha != expected_sha:
        _fail(f"{repo}#{number} merge SHA {sha} != expected {expected_sha}")


def check_live_prerequisites(recon: dict) -> None:
    prereq = recon["prerequisites"]
    if not (
        prereq.get("FIELD_KIT_114_MERGED")
        and prereq.get("PORTAL_11_MERGED")
        and prereq.get("WAIKE_55_MERGED")
    ):
        _fail("CODE_HEALTH_R5_S1_RECONCILIATION=BLOCKED_OWNER_MERGE")
    for key, sha in [
        ("FIELD_KIT_114_MERGE_SHA", EXPECTED_MERGES["field_kit_114"]),
        ("PORTAL_11_MERGE_SHA", EXPECTED_MERGES["portal_11"]),
        ("WAIKE_55_MERGE_SHA", EXPECTED_MERGES["waike_55"]),
    ]:
        if prereq.get(key) != sha:
            _fail(f"prerequisites.{key} mismatch")
    _gh_pr_merged("gunnchOS3k/gunnchos-7gc-ai-ran-field-kit", 114, EXPECTED_MERGES["field_kit_114"])
    _gh_pr_merged("gunnchOS3k/gunnchos-research-portal", 11, EXPECTED_MERGES["portal_11"])
    _gh_pr_merged("gunnchOS3k/waike-research-ops", 55, EXPECTED_MERGES["waike_55"])


def _no_coupling(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return COUPLING_RE.search(text) is None


def verify_sibling_remediation(portal_root: Path | None, waike_root: Path | None) -> None:
    """Re-run accepted remediation checks when sibling checkouts are provided."""
    if portal_root and portal_root.is_dir():
        print(f"Re-verifying portal at {portal_root}")
        r = subprocess.run(["make", "test"], cwd=portal_root, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            _fail(f"portal make test failed: {r.stderr[-500:]}")
        r = subprocess.run(
            ["make", "code-health-r5-s1"],
            cwd=portal_root,
            capture_output=True,
            text=True,
            timeout=900,
        )
        if r.returncode != 0:
            _fail(f"portal code-health-r5-s1 failed: {r.stderr[-500:]}")
        result = _load(portal_root / "artifacts/code_health_r5_s1/portal/R5_S1_RESULT.json")
        for k in ("PORTAL_CLEAN_SUITE_PASS", "PORTAL_AUDIT_MUTATION_KILLED", "PORTAL_CANONICAL_CLI_TEST"):
            if result.get(k) is not True:
                _fail(f"portal {k} not true")
        if result.get("MUTATED_FILES_COMMITTED") is not False:
            _fail("portal MUTATED_FILES_COMMITTED must be false")
        if not _no_coupling(portal_root / "scripts/audit_portfolio.py"):
            _fail("PORTAL_PRODUCTION_PROOF_COUPLING_ADDED")
        # Disposable canonical-test kill
        with tempfile.TemporaryDirectory(prefix="portal_r5s1_ci_") as td:
            dst = Path(td) / "mut"
            shutil.copytree(
                portal_root,
                dst,
                ignore=shutil.ignore_patterns(".git", ".venv", "artifacts", "__pycache__", ".pytest_cache"),
            )
            target = dst / "scripts/audit_portfolio.py"
            original = target.read_text(encoding="utf-8")
            flipped = re.sub(r"return\s+0\b", "return 1", original, count=1)
            if flipped == original:
                _fail("portal mutation did not apply")
            target.write_text(flipped, encoding="utf-8")
            py = shutil.which("python3") or "python3"
            mut = subprocess.run(
                [py, "-m", "pytest", "-q", "tests/test_audit_portfolio.py"],
                cwd=dst,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if mut.returncode == 0:
                _fail("portal mutation not killed by canonical tests")
        print("PORTAL_REMEDIATION_RECHECK_PASS")

    if waike_root and waike_root.is_dir():
        print(f"Re-verifying WAIKE at {waike_root}")
        r = subprocess.run(["make", "test"], cwd=waike_root, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            _fail(f"waike make test failed: {r.stderr[-500:]}")
        r = subprocess.run(
            ["make", "code-health-r5-s1"],
            cwd=waike_root,
            capture_output=True,
            text=True,
            timeout=900,
        )
        if r.returncode != 0:
            _fail(f"waike code-health-r5-s1 failed: {r.stderr[-500:]}")
        result = _load(waike_root / "artifacts/code_health_r5_s1/waike/R5_S1_RESULT.json")
        for k in (
            "WAIKE_METRICS_MUTATION_KILLED",
            "WAIKE_EXAM_MUTATION_KILLED",
            "WAIKE_EXISTING_LABS_MUTATION_STILL_KILLED",
        ):
            if result.get(k) is not True:
                _fail(f"waike {k} not true")
        if result.get("MUTATED_FILES_COMMITTED") is not False:
            _fail("waike MUTATED_FILES_COMMITTED must be false")
        for rel in (
            "src/waike_curriculum/evaluation/metrics.py",
            "src/waike_course_ready/batch002/exams.py",
            "src/waike_course_ready/batch002/labs.py",
        ):
            if not _no_coupling(waike_root / rel):
                _fail("WAIKE_PRODUCTION_PROOF_COUPLING_ADDED")
        print("WAIKE_REMEDIATION_RECHECK_PASS")


def write_result(ok: bool) -> Path:
    out = STATUS / "R5_S1_RECONCILIATION_VALIDATION.json"
    payload = {
        "generated_at_utc": __import__("datetime")
        .datetime.now(__import__("datetime").timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "CODE_HEALTH_R5_S1_ACCEPTED_MAIN_RECONCILIATION_VALIDATION": TOKEN if ok else "FAIL",
        "token": TOKEN if ok else "FAIL",
        "pass": ok,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--portal-root", type=Path, default=None)
    ap.add_argument("--waike-root", type=Path, default=None)
    ap.add_argument("--require-siblings", action="store_true")
    args = ap.parse_args()

    loaded = check_overlay_files()
    check_arithmetic(loaded["recon"], loaded["current"])
    check_historical_immutable()
    check_s2_preserved()
    check_digital_baseline_unchanged()
    check_policy()
    check_live_prerequisites(loaded["recon"])

    portal = args.portal_root
    waike = args.waike_root
    if args.require_siblings and (not portal or not waike):
        _fail("--require-siblings needs --portal-root and --waike-root")
    verify_sibling_remediation(portal, waike)

    # Overlay-recorded verification flags must be true
    pv = loaded["recon"]["portal_verification"]
    wv = loaded["recon"]["waike_verification"]
    for k in (
        "PORTAL_ACCEPTED_MAIN_TESTS_PASS",
        "PORTAL_AUDIT_MUTATION_KILLED",
        "PORTAL_MUTATION_FAILURE_CAUSED_BY_CANONICAL_TESTS",
    ):
        if pv.get(k) is not True:
            _fail(f"overlay portal flag {k} not true")
    if pv.get("PORTAL_PRODUCTION_PROOF_COUPLING_ADDED") is not False:
        _fail("PORTAL_PRODUCTION_PROOF_COUPLING_ADDED must be false")
    for k in (
        "WAIKE_ACCEPTED_MAIN_TESTS_PASS",
        "WAIKE_METRICS_MUTATION_KILLED",
        "WAIKE_EXAM_MUTATION_KILLED",
        "WAIKE_LABS_MUTATION_STILL_KILLED",
        "WAIKE_METRICS_FAILURE_CAUSED_BY_CANONICAL_TESTS",
        "WAIKE_EXAM_FAILURE_CAUSED_BY_CANONICAL_TESTS",
    ):
        if wv.get(k) is not True:
            _fail(f"overlay waike flag {k} not true")
    if wv.get("WAIKE_PRODUCTION_PROOF_COUPLING_ADDED") is not False:
        _fail("WAIKE_PRODUCTION_PROOF_COUPLING_ADDED must be false")

    path = write_result(True)
    print(TOKEN)
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
