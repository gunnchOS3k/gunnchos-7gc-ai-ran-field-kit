#!/usr/bin/env python3
"""Phase B.4 evidence-mapping convergence — resolve EVIDENCE_MAPPING_OPEN to zero."""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import (  # noqa: E402
    CANONICAL_REPOS,
    END_GOAL_FAMILIES,
    WORK_STATES_OPEN,
    WORK_STATES_PENDING,
)

PENDING_WORK_STATES = WORK_STATES_PENDING | {
    "PHYSICAL_PENDING",
    "HUMAN_PENDING",
    "EXTERNAL_PENDING",
    "STANDARD_PENDING",
    "CERTIFICATION_PENDING",
    "CARRIER_PENDING",
    "VENDOR_PENDING",
    "OWNER_DECISION_PENDING",
}


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) if c is not None else "" for c in row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def build_sha_freeze(repo_shas: dict[str, str], ts: str) -> dict[str, Any]:
    return {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.b4_accepted_main_sha_freeze",
        "generated_at_utc": ts,
        "phase": "PRE_ENGINEERING_HYGIENE_PHASE_B.4",
        "policy": "Every B.4 mapping decision cites these SHAs only.",
        "canonical_repo_count": len(CANONICAL_REPOS),
        "repos": [
            {
                "repository": repo,
                "origin_main_sha": repo_shas.get(repo, ""),
                "origin_main_sha12": (repo_shas.get(repo, "") or "")[:12],
            }
            for repo in CANONICAL_REPOS
        ],
    }


def b4_decision_record(b3_row: dict[str, Any], b4_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": b3_row["requirement_id"],
        "title": b3_row.get("title"),
        "primary_end_goal_family": b4_row.get("primary_end_goal_family"),
        "b3_work_state": b3_row.get("work_state"),
        "b4_work_state": b4_row.get("work_state"),
        "b4_decision": b4_row.get("work_state"),
        "b4_decision_reason": b4_row.get("resolution_reason"),
        "accepted_main_sha": b4_row.get("accepted_main_sha"),
        "implementation_evidence": b4_row.get("implementation_evidence"),
        "validation_evidence": b4_row.get("validation_evidence"),
        "evidence_confidence": b4_row.get("evidence_confidence"),
        "pending_dimensions": b4_row.get("pending_dimensions"),
        "admissible_repositories": b4_row.get("admissible_repositories"),
        "proof_identifiers": b4_row.get("proof_identifiers"),
        "discovery_terms": b4_row.get("discovery_terms"),
        "search_passes_summary": {
            k: len(v) for k, v in (b4_row.get("search_passes") or {}).items() if v
        },
    }


def build_next_digital_impl(rows: list[dict[str, Any]], limit: int = 25) -> list[dict[str, Any]]:
    pool = [r for r in rows if r.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN"]
    pool.sort(key=lambda r: (r.get("primary_end_goal_family") or 0, r.get("requirement_id") or ""))
    return [
        {
            "requirement_id": r["requirement_id"],
            "title": r.get("title"),
            "owner_repo": r.get("owner_repo"),
            "primary_end_goal_family": r.get("primary_end_goal_family"),
            "resolution_reason": r.get("resolution_reason"),
            "next_action": r.get("next_action"),
        }
        for r in pool[:limit]
    ]


def build_next_digital_validation(rows: list[dict[str, Any]], limit: int = 25) -> list[dict[str, Any]]:
    pool = [r for r in rows if r.get("work_state") == "DIGITAL_VALIDATION_OPEN"]
    pool.sort(key=lambda r: (r.get("primary_end_goal_family") or 0, r.get("requirement_id") or ""))
    return [
        {
            "requirement_id": r["requirement_id"],
            "title": r.get("title"),
            "owner_repo": r.get("owner_repo"),
            "primary_end_goal_family": r.get("primary_end_goal_family"),
            "implementation_evidence": r.get("implementation_evidence"),
            "resolution_reason": r.get("resolution_reason"),
        }
        for r in pool[:limit]
    ]


def build_non_digital_pending(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pending_rows = [r for r in rows if r.get("work_state") in PENDING_WORK_STATES]
    by_state = Counter(r["work_state"] for r in pending_rows)
    by_dim = Counter()
    for r in pending_rows:
        for d in r.get("pending_dimensions") or []:
            by_dim[d] += 1
    by_family: dict[int, int] = Counter(r.get("primary_end_goal_family") or 0 for r in pending_rows)
    return {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.non_digital_pending_register",
        "total_pending_rows": len(pending_rows),
        "work_state_counts": dict(by_state),
        "pending_dimension_counts": dict(by_dim),
        "by_primary_family": {str(k): v for k, v in sorted(by_family.items()) if k},
        "sample_rows": [
            {
                "requirement_id": r["requirement_id"],
                "title": r.get("title"),
                "work_state": r.get("work_state"),
                "pending_dimensions": r.get("pending_dimensions"),
                "primary_end_goal_family": r.get("primary_end_goal_family"),
            }
            for r in pending_rows[:50]
        ],
    }


def write_b4_artifacts(
    b3_rows: list[dict[str, Any]],
    b4_rows: list[dict[str, Any]],
    repo_shas: dict[str, str],
    totals: dict[str, int],
    ts: str,
) -> dict[str, Any]:
    mapping_open_b3 = [r for r in b3_rows if r.get("work_state") == "EVIDENCE_MAPPING_OPEN"]
    b3_by_id = {r["requirement_id"]: r for r in b3_rows}
    decisions = [
        b4_decision_record(b3_by_id[r["requirement_id"]], r)
        for r in b4_rows
        if r["requirement_id"] in b3_by_id and b3_by_id[r["requirement_id"]].get("work_state") == "EVIDENCE_MAPPING_OPEN"
    ]
    moved = Counter(d["b4_work_state"] for d in decisions)

    sha_freeze = build_sha_freeze(repo_shas, ts)
    (OUT / "B4_ACCEPTED_MAIN_SHA_FREEZE.json").write_text(json.dumps(sha_freeze, indent=2) + "\n", encoding="utf-8")

    decisions_doc = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.b4_mapping_decisions",
        "generated_at_utc": ts,
        "phase": "PRE_ENGINEERING_HYGIENE_PHASE_B.4",
        "b3_mapping_open_count": len(mapping_open_b3),
        "b4_mapping_open_count": totals.get("EVIDENCE_MAPPING_OPEN", 0),
        "rows_processed": len(decisions),
        "moved_to_state_counts": dict(moved),
        "decisions": decisions,
    }
    (OUT / "B4_MAPPING_DECISIONS.json").write_text(json.dumps(decisions_doc, indent=2) + "\n", encoding="utf-8")

    next_impl = build_next_digital_impl(b4_rows)
    next_val = build_next_digital_validation(b4_rows)
    non_digital = build_non_digital_pending(b4_rows)

    impl_doc = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.next_digital_implementation_work",
        "generated_at_utc": ts,
        "total_open": totals.get("DIGITAL_IMPLEMENTATION_OPEN", 0),
        "top_items": next_impl,
    }
    val_doc = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.next_digital_validation_work",
        "generated_at_utc": ts,
        "total_open": totals.get("DIGITAL_VALIDATION_OPEN", 0),
        "top_items": next_val,
    }
    (OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json").write_text(json.dumps(impl_doc, indent=2) + "\n", encoding="utf-8")
    (OUT / "NEXT_DIGITAL_VALIDATION_WORK.json").write_text(json.dumps(val_doc, indent=2) + "\n", encoding="utf-8")
    (OUT / "NON_DIGITAL_PENDING_REGISTER.json").write_text(json.dumps(non_digital, indent=2) + "\n", encoding="utf-8")

    fam_names = {f["id"]: f["name"] for f in END_GOAL_FAMILIES}
    moved_rows = [[k, str(v)] for k, v in sorted(moved.items(), key=lambda x: -x[1])]
    write_markdown(
        OUT / "B4_MAPPING_DECISIONS.md",
        f"""# B.4 Mapping Decisions

Generated: `{ts}`  
B.3 mapping-open rows: **{len(mapping_open_b3)}**  
B.4 mapping-open rows: **{totals.get('EVIDENCE_MAPPING_OPEN', 0)}**  
Rows processed: **{len(decisions)}**

## Moved to state

{md_table(["Work state", "Count"], moved_rows)}

See `B4_MAPPING_DECISIONS.json` for full per-row audit.
""",
    )
    write_markdown(
        OUT / "B4_ACCEPTED_MAIN_SHA_FREEZE.md",
        "# B.4 Accepted Main SHA Freeze\n\n"
        + md_table(
            ["Repository", "origin/main SHA"],
            [[r["repository"], (r["origin_main_sha"] or "")[:12]] for r in sha_freeze["repos"]],
        )
        + "\n",
    )
    write_markdown(
        OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.md",
        "# Next Digital Implementation Work\n\n"
        + f"Total DIGITAL_IMPLEMENTATION_OPEN: **{totals.get('DIGITAL_IMPLEMENTATION_OPEN', 0)}**\n\n"
        + md_table(
            ["ID", "Title", "Owner", "Family"],
            [
                [i["requirement_id"], (i.get("title") or "")[:50], i.get("owner_repo"), str(i.get("primary_end_goal_family"))]
                for i in next_impl
            ],
        )
        + "\n",
    )
    write_markdown(
        OUT / "NEXT_DIGITAL_VALIDATION_WORK.md",
        "# Next Digital Validation Work\n\n"
        + f"Total DIGITAL_VALIDATION_OPEN: **{totals.get('DIGITAL_VALIDATION_OPEN', 0)}**\n\n"
        + md_table(
            ["ID", "Title", "Owner", "Impl evidence"],
            [
                [
                    i["requirement_id"],
                    (i.get("title") or "")[:40],
                    i.get("owner_repo"),
                    (i.get("implementation_evidence") or "")[:40],
                ]
                for i in next_val
            ],
        )
        + "\n",
    )
    write_markdown(
        OUT / "NON_DIGITAL_PENDING_REGISTER.md",
        "# Non-Digital Pending Register\n\n"
        + f"Total pending rows: **{non_digital['total_pending_rows']}**\n\n"
        + md_table(["Work state", "Count"], [[k, str(v)] for k, v in sorted(non_digital["work_state_counts"].items())])
        + "\n\n"
        + md_table(["Dimension", "Count"], [[k, str(v)] for k, v in sorted(non_digital["pending_dimension_counts"].items())])
        + "\n",
    )

    return {
        "decisions_count": len(decisions),
        "moved_to_state_counts": dict(moved),
        "mapping_open_remaining": totals.get("EVIDENCE_MAPPING_OPEN", 0),
    }


def validate_b4_mapping(rows: list[dict[str, Any]], totals: dict[str, int], sha_freeze: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    mapping_open = totals.get("EVIDENCE_MAPPING_OPEN", 0)
    if mapping_open != 0:
        errors.append(f"EVIDENCE_MAPPING_OPEN={mapping_open} (expected 0)")
    if len(sha_freeze.get("repos") or []) != 17:
        errors.append("SHA freeze must cover 17 repos")
    for repo in CANONICAL_REPOS:
        rec = next((r for r in sha_freeze.get("repos") or [] if r.get("repository") == repo), None)
        if not rec or not rec.get("origin_main_sha"):
            errors.append(f"missing SHA for {repo}")
    b4_decisions_path = OUT / "B4_MAPPING_DECISIONS.json"
    if not b4_decisions_path.is_file():
        errors.append("missing B4_MAPPING_DECISIONS.json")
    else:
        doc = json.loads(b4_decisions_path.read_text(encoding="utf-8"))
        if doc.get("b3_mapping_open_count", 0) > 0 and doc.get("rows_processed", 0) != doc.get("b3_mapping_open_count"):
            errors.append("B4_MAPPING_DECISIONS missing previously mapping-open rows")
    for row in rows:
        if row.get("work_state") == "EVIDENCE_MAPPING_OPEN":
            errors.append(f"{row['requirement_id']} still EVIDENCE_MAPPING_OPEN")
    return {
        "BASELINE_V2_B4_MAPPING_VALIDATION_PASS": len(errors) == 0,
        "errors": errors,
    }


if __name__ == "__main__":
    print("Use generate_digital_ecosystem_baseline_v2.py with BASELINE_V2_PHASE=B.4", file=sys.stderr)
    sys.exit(0)
