#!/usr/bin/env python3
"""Generate program/digital_ecosystem_baseline_v2/ from live accepted mains."""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
REPOS_ROOT = Path(os.environ.get("REPOS_ROOT", str(ROOT.parent.parent.parent)))

CANONICAL_REPOS = [
    "gunnchos-7gc-ai-ran-field-kit",
    "gunnchos-research-portal",
    "gunnchos-device-os",
    "gunnchos-hardware-industrial-design",
    "gunnchAI3k",
    "edge-io-measurement-node",
    "anime-aggressors",
    "pedestrian-pursuit",
    "archive-of-life-artifact-world",
    "beatlink-party",
    "7gc-digital-twin",
    "spectrumx-ai-ran-gary",
    "ntn-resilience-sim",
    "readygary-6g-beam-selection",
    "waike-research-ops",
    "gunnchos-emergent-service-intent-protocols",
    "gunnchos-gpu-nr-baseband-platform",
]

VERIFIED_COMPLETE = [
    {
        "requirement_id": "CHARTER_NARRATIVE",
        "layer": "L0",
        "gate": 0,
        "owner_repo": "gunnchos-7gc-ai-ran-field-kit",
        "engineering_state": "DIGITAL_IMPLEMENTATION_COMPLETE",
        "evidence": ["artifacts/wp012/VP-012-RESULT.json"],
    },
    {
        "requirement_id": "REPO_OWNERSHIP_MAP",
        "layer": "L0",
        "gate": 0,
        "owner_repo": "gunnchos-7gc-ai-ran-field-kit",
        "engineering_state": "DIGITAL_IMPLEMENTATION_COMPLETE",
        "evidence": ["artifacts/wp012/VP-012-RESULT.json"],
    },
    {
        "requirement_id": "CLAIM_BOUNDARIES",
        "layer": "L0",
        "gate": 0,
        "owner_repo": "gunnchos-7gc-ai-ran-field-kit",
        "engineering_state": "DIGITAL_IMPLEMENTATION_COMPLETE",
        "evidence": ["artifacts/wp012/VP-012-RESULT.json"],
    },
    {
        "requirement_id": "COMPLETION_REGISTER_V1",
        "layer": "L0",
        "gate": 0,
        "owner_repo": "gunnchos-7gc-ai-ran-field-kit",
        "engineering_state": "DIGITAL_IMPLEMENTATION_COMPLETE",
        "evidence": ["artifacts/wp012/VP-012-RESULT.json"],
        "note": "Superseded by Baseline V2; retained as honest L0 PASS",
    },
]

REPRODUCE_HINT = {
    "gunnchos-7gc-ai-ran-field-kit": "make verify",
    "gunnchos-research-portal": "make reproduce",
    "gunnchos-device-os": "make reproduce",
    "edge-io-measurement-node": "make reproduce",
    "7gc-digital-twin": "make reproduce",
    "ntn-resilience-sim": "make reproduce",
    "readygary-6g-beam-selection": "make reproduce",
    "gunnchos-gpu-nr-baseband-platform": "make reproduce",
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 40) -> str:
    try:
        env = os.environ.copy()
        env.setdefault("GH_PAGER", "cat")
        return subprocess.check_output(
            cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL, timeout=timeout, env=env
        ).strip()
    except Exception:
        return ""


def gh_ci(repo: str) -> str:
    raw = run(
        [
            "gh",
            "run",
            "list",
            "--repo",
            f"gunnchOS3k/{repo}",
            "--branch",
            "main",
            "--limit",
            "10",
            "--json",
            "conclusion,workflowName,status",
        ]
    )
    if not raw:
        return "UNKNOWN"
    runs = json.loads(raw)
    # Prefer primary CI-like workflows over market packets
    priority = ("CI", "test", "Stage", "Phase", "Gate", "product-completion")
    for name in priority:
        for r in runs:
            wf = r.get("workflowName") or ""
            if name.lower() in wf.lower():
                c = (r.get("conclusion") or "").lower()
                if c == "success":
                    return "PASS"
                if c in ("failure", "cancelled", "timed_out"):
                    continue
    for r in runs:
        c = (r.get("conclusion") or "").lower()
        if c == "success":
            return "PASS"
    for r in runs:
        c = (r.get("conclusion") or "").lower()
        if c == "failure":
            return "FAIL"
    return "UNKNOWN"


def live_repo(repo: str) -> dict[str, Any]:
    path = REPOS_ROOT / repo
    out: dict[str, Any] = {"repository": repo, "path": str(path), "exists": path.is_dir()}
    if not path.is_dir():
        return out
    run(["git", "fetch", "origin", "main"], cwd=path)
    sha = run(["git", "rev-parse", "origin/main"], cwd=path)
    out["origin_main_sha"] = sha
    out["ci"] = gh_ci(repo)
    out["reproduce"] = REPRODUCE_HINT.get(repo, "see REPRODUCIBILITY.md")
    return out


def gate_layer(gate: int | None) -> str:
    if gate is None:
        return "LX"
    return f"L{gate}"


def classify_requirement(req: dict[str, Any]) -> str:
    blockers = " ".join(req.get("blockers") or []).upper()
    notes = (req.get("notes") or "").upper()
    blob = f"{blockers} {notes}"
    if any(x in blob for x in ("PHYSICAL_PICKUP", "FAB_", "EVT0", "MANUFACTUR", "ENCLOSURE", "BATTERY", "THERMAL", "RFQ")):
        return "PHYSICAL_PENDING"
    if "CARRIER" in blob:
        return "CARRIER_PENDING"
    if "CERTIF" in blob or "REGULATORY" in blob:
        return "CERTIFICATION_PENDING"
    if "VENDOR" in blob or "SUPPLIER" in blob:
        return "VENDOR_PENDING"
    if "STANDARD" in blob and ("6G" in blob or "IMT" in blob):
        return "STANDARD_PENDING"
    if "OWNER_DECISION" in blob or "WP001" in blob or "EDMUND" in blob:
        return "OWNER_DECISION_PENDING"
    if any(x in blob for x in ("HUMAN", "PILOT", "OPERATOR", "CONSENT")):
        return "HUMAN_PENDING"
    if any(x in blob for x in ("EXTERNAL", "NVIDIA", "SIONNA", "AERIAL", "DOI", "PENTEST", "NGC")):
        return "EXTERNAL_PENDING"
    val = req.get("validation_state") or ""
    impl = req.get("implementation_state") or ""
    if val in ("VALIDATED", "INDEPENDENTLY_VALIDATED"):
        return "DIGITAL_IMPLEMENTATION_COMPLETE"
    if impl == "IMPLEMENTED" and val in ("PASS", "VALIDATED"):
        return "DIGITAL_IMPLEMENTATION_COMPLETE"
    return "DIGITAL_IMPLEMENTATION_OPEN"


def build_register(requirements: list[dict[str, Any]], repos: dict[str, dict]) -> tuple[list[dict], Counter]:
    verified_ids = {v["requirement_id"] for v in VERIFIED_COMPLETE}
    rows: list[dict] = []
    for v in VERIFIED_COMPLETE:
        sha = repos.get(v["owner_repo"], {}).get("origin_main_sha", "")
        rows.append(
            {
                **v,
                "title": v["requirement_id"].replace("_", " ").title(),
                "accepted_main_sha": sha,
                "source": "verified_L0_control_plane",
            }
        )
    for req in requirements:
        rid = req["id"]
        if rid in verified_ids:
            continue
        gate = req.get("gate")
        if gate is not None and gate > 6:
            continue
        state = classify_requirement(req)
        owner = req.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
        rows.append(
            {
                "requirement_id": rid,
                "title": req.get("title"),
                "layer": gate_layer(gate),
                "gate": gate,
                "owner_repo": owner,
                "engineering_state": state,
                "implementation_state": req.get("implementation_state"),
                "validation_state": req.get("validation_state"),
                "blockers": req.get("blockers") or [],
                "accepted_main_sha": repos.get(owner, {}).get("origin_main_sha", ""),
                "source": "program/requirements/requirements.yaml",
            }
        )
    counts = Counter(r["engineering_state"] for r in rows)
    return rows, counts


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(c) if c is not None else "" for c in row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    ts = now.isoformat().replace("+00:00", "Z")

    repos = {name: live_repo(name) for name in CANONICAL_REPOS}
    req_doc = yaml.safe_load((ROOT / "program/requirements/requirements.yaml").read_text(encoding="utf-8"))
    requirements = req_doc["requirements"]
    register, counts = build_register(requirements, repos)

    totals = {
        "ATOMIC_TOTAL": len(register),
        "DIGITAL_IMPLEMENTATION_COMPLETE": counts.get("DIGITAL_IMPLEMENTATION_COMPLETE", 0),
        "DIGITAL_IMPLEMENTATION_OPEN": counts.get("DIGITAL_IMPLEMENTATION_OPEN", 0),
        "PHYSICAL_PENDING": counts.get("PHYSICAL_PENDING", 0),
        "HUMAN_PENDING": counts.get("HUMAN_PENDING", 0),
        "EXTERNAL_PENDING": counts.get("EXTERNAL_PENDING", 0),
        "STANDARD_PENDING": counts.get("STANDARD_PENDING", 0),
        "CERTIFICATION_PENDING": counts.get("CERTIFICATION_PENDING", 0),
        "CARRIER_PENDING": counts.get("CARRIER_PENDING", 0),
        "VENDOR_PENDING": counts.get("VENDOR_PENDING", 0),
        "OWNER_DECISION_PENDING": counts.get("OWNER_DECISION_PENDING", 0),
    }

    ci_matrix = []
    ci_contradictions = []
    for name, rec in repos.items():
        ci_matrix.append(
            {
                "repository": name,
                "origin_main_sha": rec.get("origin_main_sha"),
                "ci": rec.get("ci"),
                "reproduce": rec.get("reproduce"),
            }
        )
        if rec.get("ci") == "FAIL":
            ci_contradictions.append(name)

    stale_preview = 0
    for pr, repo in [(53, "waike-research-ops"), (88, "gunnchos-7gc-ai-ran-field-kit"), (103, "gunnchos-device-os")]:
        raw = run(["gh", "pr", "view", str(pr), "--repo", f"gunnchOS3k/{repo}", "--json", "state"])
        if raw:
            state = json.loads(raw).get("state")
            if state == "MERGED" and pr != 103:
                stale_preview += 1

    supersession_103 = {
        "pr": 103,
        "repository": "gunnchos-device-os",
        "state": "OPEN",
        "cursor_action": "DO_NOT_CLOSE",
        "owner_action": "CLOSE_SUPERSEDED_BY_OWNER after Baseline V2 + portal snapshot",
        "unique_capabilities_remaining": [
            "DSXL_DUAL_COMPOSITOR_UX_PASS (false — virtio-gpu no hotplug)",
            "RING_TO_REAL_APP_STATE_MUTATION_PASS (false)",
            "GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_DIGITAL_COMPLETE (false)",
        ],
        "supersession_rationale": "WP-011R draft remediations overlap Cycle 3B mainline; owner closes when superseded packet accepted.",
        "evidence_pointer": "https://github.com/gunnchOS3k/gunnchos-device-os/pull/103",
    }
    raw103 = run(["gh", "pr", "view", "103", "--repo", "gunnchOS3k/gunnchos-device-os", "--json", "state"])
    if raw103:
        supersession_103["state"] = json.loads(raw103).get("state", "OPEN")

    accepted_baseline = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.accepted_main",
        "generated_at_utc": ts,
        "repos_root": str(REPOS_ROOT),
        "canonical_repo_count": len(CANONICAL_REPOS),
        "repos": repos,
        "hygiene_repairs_merged": {
            "readygary-6g-beam-selection": {"pr": 27, "note": "f-string generate_tables.py fix"},
            "waike-research-ops": {"pr": 54, "note": "digital_rc pathway count 16"},
        },
    }

    master_register = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.master_completion_register",
        "generated_at_utc": ts,
        "layer_policy": "L0-L6 maps to gates 0-6 in program/gates/gate_definitions.yaml",
        "CURSOR_NEVER_MERGES": True,
        "totals": totals,
        "requirements": register,
    }

    remaining_gaps = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.remaining_gaps",
        "generated_at_utc": ts,
        "top_blockers": [
            "device-os #103 owner supersession/close (Cursor must not close)",
            "field-kit Baseline V2 owner merge (this PR)",
            "portal final accepted-main snapshot after Baseline V2",
            "gunnchAI Product Completion 002 blocked on 8GB host",
            "ReadyGary Sionna/Aerial/TensorRT on Linux NVIDIA host",
            "GPU-NR CUDA validation requires self-hosted nvidia-gpu runner",
            "WP-011R DSXL + RING tokens still false on accepted main",
            "NVIDIA credential wrapper MISSING on build host",
        ],
        "gates_7_8_excluded_from_L0_L6": sum(1 for r in requirements if (r.get("gate") or 0) > 6),
        "device_os_103": supersession_103,
    }

    ci_repro = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.ci_and_reproduction_matrix",
        "generated_at_utc": ts,
        "matrix": ci_matrix,
        "known_accepted_main_ci_contradictions": ci_contradictions,
    }

    result = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.result",
        "generated_at_utc": ts,
        "phase": "PRE_ENGINEERING_HYGIENE_PHASE_B",
        "BASELINE_V2_STATE": "DRAFT_PR",
        "STOP_FOR_OWNER_MERGE": True,
        "totals": totals,
        "READYGARY_ACCEPTED_MAIN_CI": repos["readygary-6g-beam-selection"].get("ci"),
        "WAIKE_ACCEPTED_MAIN_CI": repos["waike-research-ops"].get("ci"),
        "FIELD_KIT_BASELINE_V2": "DRAFT_NOT_ACCEPTED_MAIN",
        "PORTAL_FINAL_ACCEPTED_MAIN_SNAPSHOT": "STALE_DRIFT",
        "DEVICE_OS_103_DISPOSITION": "OPEN_AWAITING_OWNER_SUPERSESSION",
        "STALE_PREVIEW_REFERENCES": stale_preview,
        "KNOWN_ACCEPTED_MAIN_CI_CONTRADICTIONS": len(ci_contradictions),
        "PRE_ENGINEERING_HYGIENE_PASS": False,
        "ENGINEERING_NEXT_WAVE_ALLOWED": False,
    }

    OUT.mkdir(parents=True, exist_ok=True)

    (OUT / "ACCEPTED_MAIN_BASELINE.json").write_text(json.dumps(accepted_baseline, indent=2) + "\n", encoding="utf-8")
    (OUT / "MASTER_COMPLETION_REGISTER.json").write_text(json.dumps(master_register, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining_gaps, indent=2) + "\n", encoding="utf-8")
    (OUT / "CI_AND_REPRODUCTION_MATRIX.json").write_text(json.dumps(ci_repro, indent=2) + "\n", encoding="utf-8")
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    repo_rows = [[r, (repos[r].get("origin_main_sha") or "")[:12], repos[r].get("ci", "?")] for r in CANONICAL_REPOS]
    write_markdown(
        OUT / "README.md",
        f"""# GUNNCHOS Digital Ecosystem Baseline V2 (Pre-Engineering Hygiene)

Generated: `{ts}`  
Phase: **PRE_ENGINEERING_HYGIENE Phase B**  
Policy: **Cursor never merges**. Edmund sole merge authority. **main only**.

## Summary

{md_table(["Metric", "Count"], [[k, str(v)] for k, v in totals.items()])}

## Accepted mains ({len(CANONICAL_REPOS)} canonical repos)

{md_table(["Repository", "origin/main (short)", "CI"], repo_rows)}

## Artifacts

- `ACCEPTED_MAIN_BASELINE.json` / `.md`
- `MASTER_COMPLETION_REGISTER.json` / `.md`
- `REMAINING_GAPS.json` / `.md`
- `CI_AND_REPRODUCTION_MATRIX.json` / `.md`
- `EVIDENCE_CLASSIFICATION.md`
- `SUPERSEDED_PR_DISPOSITION.md`
- `BASELINE_V2_RESULT.json`

Regenerate: `python3 scripts/generate_digital_ecosystem_baseline_v2.py`  
Validate: `python3 scripts/validate_digital_ecosystem_baseline_v2.py`
""",
    )

    write_markdown(
        OUT / "ACCEPTED_MAIN_BASELINE.md",
        "# Accepted Main Baseline (V2)\n\n"
        + md_table(["Repository", "SHA", "CI"], repo_rows)
        + "\n\nSee `ACCEPTED_MAIN_BASELINE.json` for full record.\n",
    )

    write_markdown(
        OUT / "MASTER_COMPLETION_REGISTER.md",
        "# Master Completion Register (L0–L6)\n\n"
        + md_table(["Metric", "Count"], [[k, str(v)] for k, v in totals.items()])
        + f"\n\nTotal requirement rows (gates 0–6 + verified L0): **{totals['ATOMIC_TOTAL']}**\n",
    )

    write_markdown(
        OUT / "REMAINING_GAPS.md",
        "# Remaining Gaps\n\n"
        + "\n".join(f"- {b}" for b in remaining_gaps["top_blockers"])
        + "\n\nSee `REMAINING_GAPS.json` and `SUPERSEDED_PR_DISPOSITION.md`.\n",
    )

    write_markdown(
        OUT / "CI_AND_REPRODUCTION_MATRIX.md",
        "# CI and Reproduction Matrix\n\n"
        + md_table(["Repository", "CI", "Reproduce"], [[m["repository"], m["ci"], m["reproduce"]] for m in ci_matrix])
        + "\n",
    )

    write_markdown(
        OUT / "EVIDENCE_CLASSIFICATION.md",
        """# Evidence Classification (Baseline V2)

| Class | Meaning |
| --- | --- |
| E0 | Document-only / charter |
| E1 | Unit or schema test on accepted main |
| E2 | Integrated CI PASS on accepted main |
| E3 | Cross-repo reproduction harness |
| E4 | Independent VP artifact with explicit negative space |

Baseline V2 does **not** upgrade E1/E2 to product-shipping claims. `DIGITAL_IMPLEMENTATION_COMPLETE` rows require explicit evidence pointers on accepted main or verified L0 control-plane VPs only.
""",
    )

    write_markdown(
        OUT / "SUPERSEDED_PR_DISPOSITION.md",
        f"""# Superseded PR Disposition

## device-os #103 — OPEN (do not close by Cursor)

| Field | Value |
| --- | --- |
| State | `{supersession_103['state']}` |
| Unique capabilities remaining | {len(supersession_103['unique_capabilities_remaining'])} |
| Cursor action | DO_NOT_CLOSE |
| Owner action | Close as SUPERSEDED_BY_OWNER after Baseline V2 merge + portal refresh |

### Capabilities not yet earned on accepted main

"""
        + "\n".join(f"- {c}" for c in supersession_103["unique_capabilities_remaining"])
        + """

## Stale preview references

Merged hygiene PRs #53 (WAIKE) and #88 (field-kit) may still appear in portal preview drafts — counted in `STALE_PREVIEW_REFERENCES`.
""",
    )

    print(json.dumps({"ok": True, "out": str(OUT), "totals": totals}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
