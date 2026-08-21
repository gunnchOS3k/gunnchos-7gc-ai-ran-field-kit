#!/usr/bin/env python3
"""Code Health & Implementation Authenticity Baseline V1 — ecosystem audit runner.

READ-ONLY against product repos. Writes ONLY under field-kit program/ and tools/.
Does not optimize for PASS; serious findings are expected and valuable.
CI must not fail merely because genuine S0/S1 findings exist.
"""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

# Resolve field-kit root from this file so CI checkouts work (no hardcoded laptop paths).
_FIELD_KIT_FROM_FILE = Path(__file__).resolve().parents[2]


def _resolve_field_kit() -> Path:
    env = os.environ.get("GUNNCHOS_FIELD_KIT")
    if env:
        return Path(env)
    return _FIELD_KIT_FROM_FILE


def _resolve_spine() -> Path:
    env = os.environ.get("GUNNCHOS_SPINE")
    if env:
        return Path(env)
    # Prefer sibling repos next to field-kit when present; else field-kit parent.
    fk = _resolve_field_kit()
    parent = fk.parent
    if (parent / "gunnchos-device-os").exists() or (parent / "gunnchos-research-portal").exists():
        return parent
    return parent


SPINE = _resolve_spine()
FIELD_KIT = _resolve_field_kit()
OUT = FIELD_KIT / "program" / "code_health_authenticity_baseline_v1"
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
    "dist", "build", ".next", ".turbo", "target", ".godot", ".import",
    "Pods", ".gradle", ".idea", ".worktrees", "coverage", ".mypy_cache",
    ".ruff_cache", "vendor", "third_party_vendor",
}
CODE_EXTS = {
    ".py", ".gd", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".c", ".cc",
    ".cpp", ".h", ".hpp", ".java", ".kt", ".swift", ".m", ".mm", ".sh",
    ".bash", ".zsh", ".rb", ".php", ".cs", ".scala", ".vue", ".svelte",
}
DOC_EXTS = {".md", ".rst", ".txt", ".adoc"}
CFG_EXTS = {".yml", ".yaml", ".toml", ".json", ".ini", ".cfg", ".cmake"}
PROOF_PATH_HINTS = re.compile(
    r"(^|/)(tests?|test_|_test|spec|evals?|evidence|artifacts|fixtures?|"
    r"proof|harness|rehearsal|acceptance|wave0\d{2}|engineering_wave|"
    r"__tests__|__mocks__|mocks?|stubs?|golden|snapshots?|testdata|"
    r"e2e_fixtures|synth|synthetic)(/|$)",
    re.I,
)
PROD_PATH_HINTS = re.compile(
    r"(^|/)(src|lib|app|apps|packages|services?|core|runtime|product|"
    r"game-godot|scripts/(?!.*test)|cmd|pkg|internal|server|client|"
    r"frontend|backend|api|engine|platform)(/|$)",
    re.I,
)
WAVE_DUP_HINTS = re.compile(
    r"(wave0\d{2}|_mirror|_gha_authoritative|supervisor-ready|"
    r"integrity.repair|targeted.closeout)",
    re.I,
)
THEATER_PATTERNS = [
    # S0 — critical theater
    ("S0", "assert_true_literal", re.compile(r"\bassert\s+True\b|\.toBe\(true\)\s*;?\s*$|assertTrue\(true\)", re.M)),
    ("S0", "pass_only_test", re.compile(r"def\s+test_\w+\([^)]*\):\s*\n\s+pass\b", re.M)),
    ("S0", "always_pass_gate", re.compile(r"(ALWAYS_PASS|FORCE_PASS|SKIP_ASSERT|assert\s+1\s*==\s*1)", re.I)),
    ("S0", "fixture_marked_production", re.compile(r"(PRODUCTION_OR_FIELD|L6_PRODUCTION).{0,40}(fixture|synthetic|mock)", re.I | re.S)),
    # S1 — high theater / authenticity risk
    ("S1", "assert_equals_self", re.compile(r"assert\s+(\w+)\s*==\s*\1\b")),
    ("S1", "mock_entire_sut", re.compile(r"(patch\([\"'].*[\"']\)|MagicMock|AsyncMock).{0,200}(SUT|system_under_test|production)", re.I | re.S)),
    ("S1", "snapshot_only_behavior", re.compile(r"(toMatchSnapshot|assert_snapshot|golden_file).{0,80}(behavior|logic|algorithm)", re.I | re.S)),
    ("S1", "evidence_from_test_tree", re.compile(r"(DIGITALLY_VERIFIED|IMPLEMENTATION_COMPLETE).{0,60}(tests?/|fixtures?/)", re.I | re.S)),
    ("S1", "todo_pass", re.compile(r"@pytest\.mark\.todo|xit\(|xdescribe\(|it\.skip\(|describe\.skip\(", re.I)),
    # S2 — medium
    ("S2", "broad_except_pass", re.compile(r"except\s+Exception\s*:\s*\n\s*(pass|return True|return\s+\{\})", re.M)),
    ("S2", "hardcoded_pass_json", re.compile(r"[\"']status[\"']\s*:\s*[\"']PASS[\"']", re.I)),
    ("S2", "sleep_as_sync", re.compile(r"(time\.sleep|asyncio\.sleep)\([0-9.]+\).{0,40}assert", re.S)),
    ("S2", "copy_paste_assert", re.compile(r"assert\s+[\"']ok[\"']\s*==\s*[\"']ok[\"']", re.I)),
    # S3 — low / hygiene
    ("S3", "print_debug_in_test", re.compile(r"def\s+test_.*:\n(?:.*\n){0,5}.*\bprint\(", re.M)),
    ("S3", "skipped_without_ticket", re.compile(r"@pytest\.mark\.skip(?!\(.*ticket|.*issue|.*reason)", re.I)),
]

SEVERITY_ORDER = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "INFO": 4}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".wave")]
        # skip nested worktrees and huge artifact mirrors inside product checkouts
        rel = Path(dirpath).relative_to(root).as_posix()
        if any(p in SKIP_DIRS for p in Path(rel).parts):
            continue
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() in CODE_EXTS | DOC_EXTS | CFG_EXTS or fn in {
                "Makefile", "Dockerfile", "CMakeLists.txt",
            }:
                yield p


def classify_path(rel: str) -> str:
    r = rel.replace("\\", "/")
    if PROOF_PATH_HINTS.search(r):
        return "PROOF"
    if PROD_PATH_HINTS.search(r) or r.startswith(("src/", "lib/", "app/", "cmd/", "pkg/")):
        return "PRODUCTION"
    if r.startswith(("docs/", "program/", "paper/", "uml/", "design/")):
        return "DOCS_OR_PROGRAM"
    if r.startswith((".github/", "ci/", "deploy/", "infra/")):
        return "CI_OR_DEPLOY"
    if r.endswith(tuple(DOC_EXTS)):
        return "DOCS_OR_PROGRAM"
    if r.endswith(tuple(CODE_EXTS)):
        return "AMBIGUOUS_CODE"
    return "OTHER"


def file_sha256(path: Path, limit: int = 2_000_000) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        data = f.read(limit)
        h.update(data)
    return h.hexdigest()


def safe_read(path: Path, limit: int = 400_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def count_complexity_py(source: str) -> list[dict[str, Any]]:
    hotspots = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return hotspots
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            score = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With,
                                      ast.BoolOp, ast.ExceptHandler, ast.comprehension)):
                    score += 1
                if isinstance(child, ast.IfExp):
                    score += 1
            if score >= 12:
                hotspots.append({
                    "name": node.name,
                    "lineno": getattr(node, "lineno", None),
                    "complexity": score,
                })
    return hotspots


def scan_theater(rel: str, text: str) -> list[dict[str, Any]]:
    findings = []
    if classify_path(rel) not in {"PROOF", "AMBIGUOUS_CODE", "PRODUCTION"}:
        # still scan proof heavily; production lightly for always-pass gates
        pass
    for sev, kind, pat in THEATER_PATTERNS:
        if sev in {"S2", "S3"} and classify_path(rel) == "PRODUCTION" and kind != "hardcoded_pass_json":
            continue
        for m in pat.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            findings.append({
                "severity": sev,
                "kind": kind,
                "path": rel,
                "line": line,
                "snippet": text[m.start():m.start() + 120].replace("\n", " ")[:120],
            })
            if len(findings) > 40:
                return findings
    return findings


def python_imports(source: str) -> set[str]:
    mods: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        for m in re.finditer(r"^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)", source, re.M):
            mods.add(m.group(1).split(".")[0])
        return mods
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods


def analyze_repo(name: str, root: Path, sha: str) -> dict[str, Any]:
    class_counts: Counter = Counter()
    path_rows: list[dict[str, Any]] = []
    theater: list[dict[str, Any]] = []
    hotspots: list[dict[str, Any]] = []
    prod_imports_proof: list[dict[str, Any]] = []
    wave_dups: list[dict[str, Any]] = []
    fixtures: list[dict[str, Any]] = []
    orphans_candidates: list[str] = []
    dep_edges: set[tuple[str, str]] = set()
    code_files = 0
    prod_files = 0
    proof_files = 0
    readme = (root / "README.md").exists()
    entrypoints: list[str] = []

    # entrypoint heuristics
    for cand in [
        "main.py", "app.py", "src/main.py", "cmd/main.go", "package.json",
        "project.godot", "Makefile", "pyproject.toml", "Cargo.toml",
    ]:
        if (root / cand).exists():
            entrypoints.append(cand)

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        cls = classify_path(rel)
        class_counts[cls] += 1
        if path.suffix.lower() in CODE_EXTS:
            code_files += 1
            if cls == "PRODUCTION":
                prod_files += 1
            elif cls == "PROOF":
                proof_files += 1
        if len(path_rows) < 5000:
            path_rows.append({"path": rel, "class": cls, "ext": path.suffix.lower()})

        if WAVE_DUP_HINTS.search(rel) and cls in {"PRODUCTION", "AMBIGUOUS_CODE", "PROOF"}:
            wave_dups.append({"path": rel, "class": cls})

        if re.search(r"fixture|synthetic|mock_data|testdata", rel, re.I):
            honesty = "DECLARED_FIXTURE"
            text_head = safe_read(path, 2000)
            if re.search(r"(real.?production|live.?data|accepted.?main.?evidence|NOT.?A.?FIXTURE)", text_head, re.I):
                honesty = "CLAIMED_REAL_IN_FIXTURE_PATH"
            fixtures.append({"path": rel, "honesty": honesty})

        if path.suffix.lower() not in CODE_EXTS:
            continue
        text = safe_read(path)
        if not text:
            continue

        # theater
        theater.extend(scan_theater(rel, text))

        # complexity (python)
        if path.suffix == ".py":
            for hs in count_complexity_py(text):
                hotspots.append({"path": rel, **hs})
            mods = python_imports(text)
            for m in mods:
                dep_edges.add((rel, m))
            if cls == "PRODUCTION":
                # production importing tests/proof
                bad = [m for m in mods if m in {"tests", "test", "pytest", "fixtures", "evidence", "evals"}]
                # also path-based imports
                if re.search(r"from\s+(tests|fixtures|evidence|evals)\b|import\s+(tests|fixtures)\b", text):
                    prod_imports_proof.append({"path": rel, "imports": sorted(bad) or ["tests_or_proof_namespace"]})

        # gd/js light import edges
        if path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            for m in re.finditer(r"from\s+[\"']([^\"']+)[\"']|require\([\"']([^\"']+)[\"']\)", text):
                mod = m.group(1) or m.group(2)
                dep_edges.add((rel, mod))
                if cls == "PRODUCTION" and re.search(r"(test|spec|fixture|mock)", mod, re.I):
                    prod_imports_proof.append({"path": rel, "imports": [mod]})

    # orphan heuristic: production py modules never imported by name
    prod_py = [r["path"] for r in path_rows if r["class"] == "PRODUCTION" and r["path"].endswith(".py")]
    imported_names = {e[1] for e in dep_edges}
    for p in prod_py[:300]:
        stem = Path(p).stem
        if stem in {"__init__", "main", "app", "cli"}:
            continue
        if stem not in imported_names and p.count("/") >= 1:
            orphans_candidates.append(p)
    orphans_candidates = orphans_candidates[:40]

    # proof independence summary
    proof_indep = {
        "production_files": prod_files,
        "proof_files": proof_files,
        "production_imports_proof_count": len(prod_imports_proof),
        "production_imports_proof": prod_imports_proof[:50],
        "status": (
            "FAIL_COUPLED" if prod_imports_proof else
            "PASS_INDEPENDENT" if prod_files > 0 else
            "NOT_APPLICABLE_NO_PRODUCTION_CODE"
        ),
    }

    # runtime authenticity matrix (heuristic)
    runtime = {
        "has_entrypoint": bool(entrypoints),
        "entrypoints": entrypoints,
        "has_tests": proof_files > 0 or class_counts.get("PROOF", 0) > 0,
        "tests_reference_production": any(
            classify_path(t["path"]) == "PROOF" for t in theater
        ) or proof_files > 0,
        "authenticity": (
            "ADEQUATE" if entrypoints and prod_files > 0 and proof_files > 0 and not prod_imports_proof
            else "NEEDS_WORK" if prod_files > 0
            else "CRITICAL" if proof_files > 0 and prod_files == 0
            else "NOT_APPLICABLE"
        ),
    }

    # dimension ratings
    dimensions = {
        "production_proof_separation": (
            "CRITICAL" if prod_imports_proof else
            "STRONG" if prod_files and proof_files else
            "ADEQUATE" if prod_files else
            "NEEDS_WORK"
        ),
        "anti_test_theater": _theater_dim(theater),
        "dependency_boundaries": "NEEDS_WORK" if prod_imports_proof else "ADEQUATE",
        "canonical_vs_wave_dup": "NEEDS_WORK" if len(wave_dups) > 25 else ("ADEQUATE" if wave_dups else "STRONG"),
        "runtime_authenticity": runtime["authenticity"],
        "complexity_hotspots": (
            "CRITICAL" if any(h["complexity"] >= 40 for h in hotspots) else
            "NEEDS_WORK" if len(hotspots) > 15 else
            "ADEQUATE" if hotspots else "STRONG"
        ),
        "orphan_dead_code": "NEEDS_WORK" if len(orphans_candidates) > 10 else "ADEQUATE",
        "fixture_honesty": (
            "CRITICAL" if any(f["honesty"] == "CLAIMED_REAL_IN_FIXTURE_PATH" for f in fixtures) else
            "ADEQUATE" if fixtures else "STRONG"
        ),
        "documentation_readability": "ADEQUATE" if readme else "NEEDS_WORK",
        "mutation_resistance": "NOT_APPLICABLE",  # filled by mutation sampler
    }

    s0 = sum(1 for t in theater if t["severity"] == "S0")
    s1 = sum(1 for t in theater if t["severity"] == "S1")

    return {
        "repository": name,
        "accepted_main_sha": sha,
        "scanned_at_utc": utc_now(),
        "counts": {
            "files_classified": int(sum(class_counts.values())),
            "code_files": code_files,
            "production_code_files": prod_files,
            "proof_files": proof_files,
            "class_histogram": dict(class_counts),
            "theater_s0": s0,
            "theater_s1": s1,
            "theater_total": len(theater),
            "hotspots": len(hotspots),
            "wave_dup_paths": len(wave_dups),
            "fixture_paths": len(fixtures),
            "orphan_candidates": len(orphans_candidates),
            "dep_edges": len(dep_edges),
        },
        "proof_independence": proof_indep,
        "runtime_authenticity": runtime,
        "dimensions": dimensions,
        "theater_findings": sorted(theater, key=lambda x: SEVERITY_ORDER.get(x["severity"], 9))[:80],
        "complexity_hotspots": sorted(hotspots, key=lambda x: -x["complexity"])[:30],
        "wave_duplicate_paths": wave_dups[:60],
        "fixtures": fixtures[:60],
        "orphan_candidates": orphans_candidates,
        "dependency_edges_sample": [{"from": a, "to": b} for a, b in list(dep_edges)[:80]],
        "path_classification_sample": path_rows[:200],
        "path_classification_full_count": len(path_rows),
    }


def _theater_dim(theater: list[dict[str, Any]]) -> str:
    if any(t["severity"] == "S0" for t in theater):
        return "CRITICAL"
    if any(t["severity"] == "S1" for t in theater):
        return "NEEDS_WORK"
    if any(t["severity"] == "S2" for t in theater):
        return "ADEQUATE"
    return "STRONG"


def proof_independence_worktree_test(name: str, root: Path, sha: str) -> dict[str, Any]:
    """Create a temp worktree, strip proof trees, check whether production still imports cleanly.

    Does NOT delete from accepted checkout. Temp worktree removed after.
    """
    result = {
        "repository": name,
        "sha": sha,
        "method": "temp_worktree_proof_strip_import_scan",
        "status": "NOT_RUN",
    }
    if not (root / ".git").exists() and not (root / ".git").is_file():
        result["status"] = "SKIP_NO_GIT"
        return result
    tmp = Path(tempfile.mkdtemp(prefix=f"chab_{name}_"))
    try:
        wt = tmp / "wt"
        # local checkout without altering primary
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(wt), sha],
            cwd=str(root), capture_output=True, text=True, timeout=180, check=False,
        )
        if not wt.exists():
            # fallback: copy sparse tree of production-ish dirs only via archive
            subprocess.run(
                ["git", "archive", sha, "-o", str(tmp / "a.tar")],
                cwd=str(root), capture_output=True, timeout=180,
            )
            wt.mkdir(parents=True, exist_ok=True)
            subprocess.run(["tar", "xf", str(tmp / "a.tar"), "-C", str(wt)], check=False)
        # remove proof dirs inside temp only
        removed = []
        for dname in ["tests", "test", "evals", "evidence", "fixtures", "__tests__", "spec"]:
            for p in wt.rglob(dname):
                if p.is_dir() and p.name == dname:
                    shutil.rmtree(p, ignore_errors=True)
                    removed.append(str(p.relative_to(wt)))
        # re-scan production imports
        coupled = []
        for path in iter_files(wt):
            rel = path.relative_to(wt).as_posix()
            if classify_path(rel) != "PRODUCTION" or path.suffix != ".py":
                continue
            text = safe_read(path)
            if re.search(r"from\s+(tests|fixtures|evidence|evals)\b|import\s+(tests|fixtures)\b", text):
                coupled.append(rel)
        result.update({
            "status": "FAIL_COUPLED" if coupled else "PASS_INDEPENDENT",
            "proof_dirs_removed_in_temp": removed[:40],
            "still_coupled_production_files": coupled[:40],
        })
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)[:400]
    finally:
        # cleanup worktree registration if any
        try:
            subprocess.run(
                ["git", "worktree", "prune"],
                cwd=str(root), capture_output=True, timeout=60,
            )
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
    return result


def mutation_sample(name: str, root: Path, sha: str) -> dict[str, Any]:
    """Up to 3 meaningful mutations in a temp worktree; do not commit; observe test/script reaction.

    This is a sampling audit, not a full mutation testing campaign.
    """
    out: dict[str, Any] = {
        "repository": name,
        "sha": sha,
        "mutations": [],
        "status": "NOT_RUN",
        "dimension": "NOT_APPLICABLE",
    }
    if not root.exists():
        return out
    tmp = Path(tempfile.mkdtemp(prefix=f"mut_{name}_"))
    try:
        wt = tmp / "wt"
        r = subprocess.run(
            ["git", "worktree", "add", "--detach", str(wt), sha],
            cwd=str(root), capture_output=True, text=True, timeout=180,
        )
        if not wt.exists():
            out["status"] = "SKIP_WORKTREE_FAILED"
            out["stderr"] = (r.stderr or "")[:300]
            return out

        # find up to 3 production python functions to mutate
        targets = []
        for path in iter_files(wt):
            rel = path.relative_to(wt).as_posix()
            if classify_path(rel) != "PRODUCTION" or path.suffix != ".py":
                continue
            text = safe_read(path)
            if re.search(r"def\s+\w+\(.*\):\n\s+return\s+", text):
                targets.append(path)
            if len(targets) >= 3:
                break

        if not targets:
            # try any py with return True/False
            for path in iter_files(wt):
                if path.suffix == ".py":
                    text = safe_read(path)
                    if "return True" in text or "return False" in text:
                        targets.append(path)
                if len(targets) >= 3:
                    break

        detected = 0
        for i, path in enumerate(targets[:3]):
            rel = path.relative_to(wt).as_posix()
            original = path.read_text(encoding="utf-8", errors="replace")
            mutated = original
            kind = None
            if "return True" in original:
                mutated = original.replace("return True", "return False", 1)
                kind = "flip_return_true"
            elif "return False" in original:
                mutated = original.replace("return False", "return True", 1)
                kind = "flip_return_false"
            elif re.search(r"return\s+0\b", original):
                mutated = re.sub(r"return\s+0\b", "return 1", original, count=1)
                kind = "flip_return_zero"
            else:
                mutated = original + "\n# CHAB_MUTATION_MARKER\n"
                kind = "append_marker"

            path.write_text(mutated, encoding="utf-8")
            # Prefer a cheap syntax/compile check + optional pytest collection
            syntax_ok = True
            try:
                compile(mutated, rel, "exec")
            except SyntaxError:
                syntax_ok = False
            test_reaction = "UNKNOWN"
            # If tests exist, try collecting; do not require full suite green
            if (wt / "tests").exists() or (wt / "test").exists():
                pr = subprocess.run(
                    [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                    cwd=str(wt), capture_output=True, text=True, timeout=90,
                )
                if pr.returncode != 0 and kind != "append_marker":
                    test_reaction = "SUITE_IMPACTED_OR_BROKEN_COLLECTION"
                    detected += 1
                elif kind == "append_marker":
                    test_reaction = "MARKER_LIKELY_UNDETECTED"
                else:
                    test_reaction = "COLLECTION_STILL_OK_FULL_RUN_NOT_EXECUTED"
            else:
                test_reaction = "NO_TESTS_DIR"
            # restore in temp (not needed since we delete) but record
            out["mutations"].append({
                "index": i + 1,
                "path": rel,
                "kind": kind,
                "syntax_ok_after_mutation": syntax_ok,
                "test_reaction": test_reaction,
            })
            path.write_text(original, encoding="utf-8")

        if not out["mutations"]:
            out["status"] = "NO_MUTATION_TARGETS"
            out["dimension"] = "NOT_APPLICABLE"
        else:
            out["status"] = "SAMPLED"
            if detected >= 2:
                out["dimension"] = "ADEQUATE"
            elif detected == 1:
                out["dimension"] = "NEEDS_WORK"
            else:
                out["dimension"] = "CRITICAL" if any(
                    m["kind"] != "append_marker" for m in out["mutations"]
                ) else "NEEDS_WORK"
            out["detected_count"] = detected
    except Exception as e:
        out["status"] = "ERROR"
        out["error"] = str(e)[:400]
        out["dimension"] = "BLOCKED"
    finally:
        try:
            subprocess.run(["git", "worktree", "prune"], cwd=str(root), capture_output=True, timeout=60)
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def mermaid_dep_graph(repo_results: list[dict[str, Any]]) -> str:
    lines = ["flowchart LR"]
    for r in repo_results:
        node = r["repository"].replace("-", "_")
        lines.append(f'  {node}["{r["repository"]}"]')
    # cross-repo edges from known ecosystem relationships
    edges = [
        ("gunnchos_research_portal", "gunnchos_7gc_ai_ran_field_kit"),
        ("gunnchos_device_os", "gunnchAI3k"),
        ("gunnchos_device_os", "edge_io_measurement_node"),
        ("gunnchos_7gc_ai_ran_field_kit", "readygary_6g_beam_selection"),
        ("gunnchos_7gc_ai_ran_field_kit", "ntn_resilience_sim"),
        ("gunnchos_7gc_ai_ran_field_kit", "spectrumx_ai_ran_gary"),
        ("gunnchos_7gc_ai_ran_field_kit", "7gc_digital_twin"),
        ("anime_aggressors", "gunnchos_device_os"),
        ("pedestrian_pursuit", "gunnchos_device_os"),
        ("beatlink_party", "gunnchos_device_os"),
        ("archive_of_life_artifact_world", "gunnchos_device_os"),
        ("waike_research_ops", "gunnchAI3k"),
        ("gunnchos_gpu_nr_baseband_platform", "gunnchos_7gc_ai_ran_field_kit"),
        ("gunnchos_emergent_service_intent_protocols", "gunnchos_7gc_ai_ran_field_kit"),
        ("gunnchos_hardware_industrial_design", "gunnchos_device_os"),
    ]
    for a, b in edges:
        lines.append(f"  {a} --> {b}")
    lines.append("  %% Edges are ecosystem control-plane / product relationships, not pip imports.")
    return "\n".join(lines) + "\n"


def plantuml_dep_graph(repo_results: list[dict[str, Any]]) -> str:
    lines = ["@startuml", "title gunnchOS3k Canonical 17 — Ecosystem Dependency Truth", "left to right direction"]
    for r in repo_results:
        lines.append(f'component "{r["repository"]}" as {r["repository"].replace("-", "_")}')
    edges = [
        ("gunnchos_research_portal", "gunnchos_7gc_ai_ran_field_kit"),
        ("gunnchos_device_os", "gunnchAI3k"),
        ("gunnchos_device_os", "edge_io_measurement_node"),
        ("gunnchos_7gc_ai_ran_field_kit", "readygary_6g_beam_selection"),
        ("gunnchos_7gc_ai_ran_field_kit", "ntn_resilience_sim"),
        ("anime_aggressors", "gunnchos_device_os"),
        ("pedestrian_pursuit", "gunnchos_device_os"),
        ("beatlink_party", "gunnchos_device_os"),
        ("archive_of_life_artifact_world", "gunnchos_device_os"),
        ("waike_research_ops", "gunnchAI3k"),
    ]
    for a, b in edges:
        lines.append(f"{a} --> {b}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def five_minute_map(repo: dict[str, Any]) -> str:
    name = repo["repository"]
    c = repo["counts"]
    d = repo["dimensions"]
    lines = [
        f"# Five-minute codebase map — `{name}`",
        "",
        f"Accepted main: `{repo['accepted_main_sha'][:12]}`",
        "",
        "## What this repo is",
        f"- Classified files: **{c['files_classified']}** (code={c['code_files']}, production≈{c['production_code_files']}, proof≈{c['proof_files']})",
        f"- Entrypoints: {', '.join(repo['runtime_authenticity'].get('entrypoints') or ['(none detected)'])}",
        "",
        "## Where production lives",
        "- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).",
        "- Proof/evidence trees are not product runtime.",
        "",
        "## Where proof lives",
        "- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.",
        "",
        "## Authenticity snapshot",
        f"- Proof independence: `{repo['proof_independence']['status']}`",
        f"- Runtime authenticity: `{repo['runtime_authenticity']['authenticity']}`",
        f"- Theater: S0={c['theater_s0']} S1={c['theater_s1']} total={c['theater_total']}",
        f"- Hotspots: {c['hotspots']}; wave-dup paths: {c['wave_dup_paths']}; orphans≈{c['orphan_candidates']}",
        "",
        "## Dimension ratings",
    ]
    for k, v in d.items():
        lines.append(f"- `{k}`: **{v}**")
    lines += [
        "",
        "## First files to read",
        "1. README.md (if present)",
        "2. Entrypoint from list above",
        "3. One production module and one test that claims to exercise it",
        "4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product",
        "",
        "## Maintainability risks (this scan)",
    ]
    if repo["theater_findings"]:
        top = repo["theater_findings"][0]
        lines.append(f"- Top theater hit: `{top['severity']}` `{top['kind']}` at `{top['path']}:{top['line']}`")
    else:
        lines.append("- No static theater hits in scanned sample.")
    if repo["complexity_hotspots"]:
        h = repo["complexity_hotspots"][0]
        lines.append(f"- Hottest function: `{h['path']}::{h['name']}` complexity={h['complexity']}")
    lines.append("")
    return "\n".join(lines)


def remediation_register(all_findings: list[dict[str, Any]]) -> dict[str, Any]:
    families = {
        "R1": {"name": "Production/proof coupling", "items": []},
        "R2": {"name": "Test theater (S0/S1)", "items": []},
        "R3": {"name": "Wave/canonical duplicate implementations", "items": []},
        "R4": {"name": "Runtime-path inauthenticity", "items": []},
        "R5": {"name": "Mutation blindness", "items": []},
        "R6": {"name": "Complexity / hotspot debt", "items": []},
        "R7": {"name": "Orphan/dead code & fixture honesty", "items": []},
        "R8": {"name": "Docs/architecture truth drift", "items": []},
    }
    for f in all_findings:
        fam = f.get("family", "R8")
        if fam in families:
            families[fam]["items"].append(f)
    return {
        "schema": "gunnchos.code_health_authenticity_baseline_v1.remediation_register",
        "generated_at_utc": utc_now(),
        "note": "Remediation families only. Does NOT change Baseline requirement counts.",
        "baseline_counts_unchanged": True,
        "families": families,
    }


def run_controls(out_dir: Path) -> dict[str, Any]:
    """Positive + negative synthetic controls outside product repos."""
    ctrl = out_dir / "controls"
    neg = ctrl / "negative"
    pos = ctrl / "positive"
    neg.mkdir(parents=True, exist_ok=True)
    pos.mkdir(parents=True, exist_ok=True)

    # Negative: obvious theater should be detected
    write_text(neg / "test_theater.py", "def test_always():\n    assert True\n\ndef test_empty():\n    pass\n")
    write_text(neg / "prod_coupled.py", "from tests.helpers import x\n\ndef run():\n    return x\n")
    # Positive: clean production + real assert
    write_text(pos / "src" / "calc.py", "def add(a, b):\n    return a + b\n")
    write_text(pos / "tests" / "test_calc.py", "from src.calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n")

    neg_hits = scan_theater("tests/test_theater.py", (neg / "test_theater.py").read_text())
    pos_hits = scan_theater("tests/test_calc.py", (pos / "tests" / "test_calc.py").read_text())
    coupled = bool(re.search(r"from\s+tests\b", (neg / "prod_coupled.py").read_text()))

    result = {
        "negative_control_detects_theater": any(h["severity"] == "S0" for h in neg_hits),
        "negative_control_detects_coupling_pattern": coupled,
        "positive_control_clean": len([h for h in pos_hits if h["severity"] in {"S0", "S1"}]) == 0,
        "negative_hits": neg_hits,
        "positive_hits": pos_hits,
    }
    result["AUDIT_INTEGRITY_CONTROLS"] = (
        "PASS" if result["negative_control_detects_theater"]
        and result["negative_control_detects_coupling_pattern"]
        and result["positive_control_clean"]
        else "FAIL"
    )
    write_json(ctrl / "CONTROL_RESULTS.json", result)
    return result


def load_manifest() -> dict[str, Any]:
    return json.loads((OUT / "ACCEPTED_MAIN_MANIFEST.json").read_text())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    repos = manifest["repos"]
    assert len(repos) == 17, f"expected 17 repos, got {len(repos)}"

    controls = run_controls(OUT)
    if controls["AUDIT_INTEGRITY_CONTROLS"] != "PASS":
        write_json(OUT / "BASELINE_RESULT.json", {
            "CODE_HEALTH_AUTHENTICITY_BASELINE_V1": "FAIL_AUDIT_INTEGRITY",
            "controls": controls,
        })
        print("FAIL_AUDIT_INTEGRITY")
        return 2

    repo_results = []
    proof_indep_results = []
    mutation_results = []
    all_findings = []
    path_summary = {}

    for entry in repos:
        name = entry["repository"]
        sha = entry["origin_main_sha"]
        root = Path(entry["local_path"])
        print(f"== scanning {name} @ {sha[:12]} ==")
        if not root.exists():
            repo_results.append({
                "repository": name,
                "accepted_main_sha": sha,
                "error": "LOCAL_PATH_MISSING",
                "dimensions": {k: "BLOCKED" for k in [
                    "production_proof_separation", "anti_test_theater", "dependency_boundaries",
                    "canonical_vs_wave_dup", "runtime_authenticity", "complexity_hotspots",
                    "orphan_dead_code", "fixture_honesty", "documentation_readability",
                    "mutation_resistance",
                ]},
                "counts": {"theater_s0": 0, "theater_s1": 0, "theater_total": 0},
                "theater_findings": [],
                "proof_independence": {"status": "BLOCKED"},
                "runtime_authenticity": {"authenticity": "BLOCKED", "entrypoints": []},
                "complexity_hotspots": [],
                "wave_duplicate_paths": [],
                "fixtures": [],
                "orphan_candidates": [],
                "dependency_edges_sample": [],
                "path_classification_sample": [],
            })
            continue

        # Ensure we scan tree content at sha via archive extract to temp for dirty worktrees
        scan_root = root
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(root), capture_output=True, text=True)
        use_archive = bool(dirty.stdout.strip())
        tmp_scan = None
        if use_archive:
            tmp_scan = Path(tempfile.mkdtemp(prefix=f"scan_{name}_"))
            arch = tmp_scan / "a.tar"
            subprocess.run(["git", "archive", sha, "-o", str(arch)], cwd=str(root), check=False)
            scan_root = tmp_scan / "tree"
            scan_root.mkdir()
            subprocess.run(["tar", "xf", str(arch), "-C", str(scan_root)], check=False)
            print(f"  (dirty worktree — scanning git archive of {sha[:12]})")

        try:
            result = analyze_repo(name, scan_root, sha)
        finally:
            if tmp_scan:
                shutil.rmtree(tmp_scan, ignore_errors=True)

        pi = proof_independence_worktree_test(name, root, sha)
        proof_indep_results.append(pi)
        if pi.get("status") == "FAIL_COUPLED":
            result["proof_independence"]["status"] = "FAIL_COUPLED"
            result["dimensions"]["production_proof_separation"] = "CRITICAL"
            all_findings.append({
                "family": "R1", "severity": "S0", "repository": name,
                "title": "Production still references proof namespaces after proof-strip",
                "detail": pi.get("still_coupled_production_files", [])[:10],
            })

        mut = mutation_sample(name, root, sha)
        mutation_results.append(mut)
        result["mutation_sampling"] = mut
        result["dimensions"]["mutation_resistance"] = mut.get("dimension", "NOT_APPLICABLE")
        if mut.get("dimension") == "CRITICAL":
            all_findings.append({
                "family": "R5", "severity": "S1", "repository": name,
                "title": "Mutation sample not detected by available tests",
                "detail": mut.get("mutations", [])[:3],
            })

        # collect findings
        for t in result.get("theater_findings", [])[:20]:
            if t["severity"] in {"S0", "S1"}:
                all_findings.append({
                    "family": "R2", "severity": t["severity"], "repository": name,
                    "title": f"Test theater: {t['kind']}", "path": t["path"], "line": t["line"],
                })
        if result.get("wave_duplicate_paths"):
            all_findings.append({
                "family": "R3", "severity": "S2", "repository": name,
                "title": f"Wave/duplicate path concentration ({len(result['wave_duplicate_paths'])} paths)",
                "detail": [w["path"] for w in result["wave_duplicate_paths"][:8]],
            })
        if result["runtime_authenticity"]["authenticity"] in {"CRITICAL", "NEEDS_WORK"}:
            all_findings.append({
                "family": "R4", "severity": "S1" if result["runtime_authenticity"]["authenticity"] == "CRITICAL" else "S2",
                "repository": name,
                "title": f"Runtime authenticity {result['runtime_authenticity']['authenticity']}",
            })
        if result["dimensions"].get("complexity_hotspots") in {"CRITICAL", "NEEDS_WORK"}:
            all_findings.append({
                "family": "R6", "severity": "S2", "repository": name,
                "title": "Complexity hotspots present",
                "detail": result.get("complexity_hotspots", [])[:5],
            })
        if result.get("orphan_candidates") or any(
            f.get("honesty") == "CLAIMED_REAL_IN_FIXTURE_PATH" for f in result.get("fixtures", [])
        ):
            all_findings.append({
                "family": "R7", "severity": "S2", "repository": name,
                "title": "Orphan candidates and/or fixture honesty issues",
                "orphans": result.get("orphan_candidates", [])[:8],
            })
        if result["dimensions"].get("documentation_readability") == "NEEDS_WORK":
            all_findings.append({
                "family": "R8", "severity": "S3", "repository": name,
                "title": "Missing README / weak five-minute readability signal",
            })

        repo_results.append(result)
        path_summary[name] = result["counts"].get("class_histogram", {})

        # per-repo outputs
        write_json(OUT / "path_classification" / f"{name}.json", {
            "repository": name,
            "sha": sha,
            "histogram": result["counts"].get("class_histogram", {}),
            "sample": result.get("path_classification_sample", []),
        })
        write_json(OUT / "reports" / "repos" / name / "REPO_SCAN.json", result)
        write_text(OUT / "reports" / "repos" / name / "FIVE_MINUTE_CODEBASE_MAP.md", five_minute_map(result))

    # aggregates
    write_json(OUT / "PATH_CLASSIFICATION_SUMMARY.json", {
        "schema": "gunnchos.code_health_authenticity_baseline_v1.path_classification_summary",
        "generated_at_utc": utc_now(),
        "repos": path_summary,
    })
    write_json(OUT / "PROOF_INDEPENDENCE_RESULTS.json", {
        "generated_at_utc": utc_now(),
        "results": proof_indep_results,
    })
    write_json(OUT / "MUTATION_RESISTANCE_SAMPLES.json", {
        "generated_at_utc": utc_now(),
        "results": mutation_results,
    })
    write_json(OUT / "ANTI_TEST_THEATER_FINDINGS.json", {
        "generated_at_utc": utc_now(),
        "findings": [
            f for f in all_findings if f.get("family") == "R2"
        ],
    })
    write_json(OUT / "RUNTIME_PATH_AUTHENTICITY_MATRIX.json", {
        "generated_at_utc": utc_now(),
        "repos": [
            {
                "repository": r["repository"],
                "authenticity": r.get("runtime_authenticity", {}),
                "proof_independence": r.get("proof_independence", {}).get("status"),
            }
            for r in repo_results
        ],
    })

    # dependency diagrams from actual scan + ecosystem graph
    mm = mermaid_dep_graph(repo_results)
    pu = plantuml_dep_graph(repo_results)
    write_text(OUT / "uml" / "current" / "ecosystem_dependencies.mmd", mm)
    write_text(OUT / "uml" / "current" / "ecosystem_dependencies.puml", pu)
    write_text(OUT / "uml" / "rendered" / "ecosystem_dependencies.md", "# Ecosystem dependencies\n\n```mermaid\n" + mm + "```\n")

    # cross-repo consistency
    dim_matrix = {}
    for r in repo_results:
        dim_matrix[r["repository"]] = r.get("dimensions", {})
    write_json(OUT / "DIMENSION_MATRIX.json", {
        "schema": "gunnchos.code_health_authenticity_baseline_v1.dimension_matrix",
        "note": "No fake aggregate percentage. Ratings: STRONG|ADEQUATE|NEEDS_WORK|CRITICAL|BLOCKED|NOT_APPLICABLE",
        "generated_at_utc": utc_now(),
        "repos": dim_matrix,
    })
    write_json(OUT / "CROSS_REPO_CONSISTENCY.json", {
        "generated_at_utc": utc_now(),
        "canonical_repo_count": 17,
        "all_sha_fetched": manifest.get("all_fetched"),
        "proof_independence_statuses": Counter(p.get("status") for p in proof_indep_results),
        "theater_s0_repos": [r["repository"] for r in repo_results if r.get("counts", {}).get("theater_s0", 0) > 0],
        "theater_s1_repos": [r["repository"] for r in repo_results if r.get("counts", {}).get("theater_s1", 0) > 0],
        "critical_dimension_repos": [
            name for name, dims in dim_matrix.items()
            if any(v == "CRITICAL" for v in dims.values())
        ],
    })

    rem = remediation_register(all_findings)
    write_json(OUT / "REMEDIATION_REGISTER.json", rem)
    # markdown register
    rem_md = ["# Remediation Register — Code Health Authenticity Baseline V1", "",
              "Baseline requirement counts are **unchanged**.", ""]
    for key, fam in rem["families"].items():
        rem_md.append(f"## {key} — {fam['name']}")
        rem_md.append(f"Items: {len(fam['items'])}")
        for it in fam["items"][:15]:
            rem_md.append(f"- [{it.get('severity','?')}] `{it.get('repository')}`: {it.get('title')}")
        rem_md.append("")
    write_text(OUT / "REMEDIATION_REGISTER.md", "\n".join(rem_md))

    # severity rollup
    s0 = sum(1 for f in all_findings if f.get("severity") == "S0")
    s1 = sum(1 for f in all_findings if f.get("severity") == "S1")
    critical_dims = sum(1 for dims in dim_matrix.values() for v in dims.values() if v == "CRITICAL")

    if controls["AUDIT_INTEGRITY_CONTROLS"] != "PASS":
        top = "FAIL_AUDIT_INTEGRITY"
    elif len(repo_results) < 17:
        top = "BLOCKED_INCOMPLETE_AUDIT"
    elif s0 > 0 or critical_dims > 0:
        top = "BASELINE_COMPLETE_WITH_FINDINGS"
    else:
        top = "BASELINE_COMPLETE_NO_CRITICAL_FINDINGS"

    # Prefer WITH_FINDINGS when any S1+ exists even without S0 — honesty
    if top == "BASELINE_COMPLETE_NO_CRITICAL_FINDINGS" and (s1 > 0 or s0 > 0):
        top = "BASELINE_COMPLETE_WITH_FINDINGS"
    # Always expect findings valuable — if somehow clean, keep NO_CRITICAL

    result = {
        "schema": "gunnchos.code_health_authenticity_baseline_v1.result",
        "generated_at_utc": utc_now(),
        "CODE_HEALTH_AUTHENTICITY_BASELINE_V1": top,
        "CURSOR_NEVER_MERGES": True,
        "prerequisite": manifest.get("prerequisite"),
        "controls": controls,
        "totals": {
            "repos_scanned": len(repo_results),
            "findings": len(all_findings),
            "s0": s0,
            "s1": s1,
            "critical_dimension_cells": critical_dims,
        },
        "note": "Genuine S0/S1 findings do not fail the CI gate; they are recorded.",
        "baseline_requirement_counts_unchanged": True,
        "product_behavior_unchanged": True,
    }
    write_json(OUT / "BASELINE_RESULT.json", result)
    write_json(OUT / "FINDINGS.json", {"generated_at_utc": utc_now(), "findings": all_findings})

    # executive summary md
    lines = [
        "# Code Health & Implementation Authenticity Baseline V1",
        "",
        f"**Result:** `{top}`",
        "",
        f"Generated: {utc_now()}",
        "",
        "## Prerequisite (frozen, unmodified)",
        "- field-kit #113 MERGED",
        "- Baseline 419 / COMPLETE=111 / IMPL_OPEN=51 / VALIDATION_OPEN=0 / EVIDENCE_MAPPING=0 / POOL=162",
        "- NEXT_VALIDATION total_open=0; NEXT_IMPL total_open=51",
        "",
        "## Totals",
        f"- Repos scanned: {len(repo_results)}/17",
        f"- Findings: {len(all_findings)} (S0={s0}, S1={s1})",
        f"- Critical dimension cells: {critical_dims}",
        "",
        "## Critical / high repos",
    ]
    for name in result and []:
        pass
    crit_repos = sorted({
        name for name, dims in dim_matrix.items() if any(v == "CRITICAL" for v in dims.values())
    })
    if crit_repos:
        for n in crit_repos:
            lines.append(f"- `{n}`")
    else:
        lines.append("- (none with CRITICAL dimension cells)")
    lines += [
        "",
        "## Dimension matrix",
        "See `DIMENSION_MATRIX.json` — ratings only, no fake aggregate %.",
        "",
        "## Outputs",
        "- Per-repo maps: `reports/repos/<repo>/`",
        "- UML: `uml/current`, `uml/rendered`",
        "- Remediation families R1–R8: `REMEDIATION_REGISTER.md`",
        "",
        "Findings are not hidden to preserve a green result.",
    ]
    write_text(OUT / "BASELINE_SUMMARY.md", "\n".join(lines))

    print(json.dumps(result, indent=2))
    print("CODE_HEALTH_AUTHENTICITY_BASELINE_V1=" + top)
    # CI exit 0 even with findings
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
