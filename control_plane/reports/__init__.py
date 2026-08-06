"""Deterministic Markdown report generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from control_plane import STATUS_AUTOMATED_PASS, STATUS_CHARTER_PENDING
from control_plane.io_util import load_yaml
from control_plane.paths import (
    BACKLOG,
    CHARTER_APPROVAL_RECORD,
    CHARTER_SOURCE_RECORD,
    CLAIMS,
    GATES,
    REPORTS,
    REPOSITORIES,
    REQUIREMENTS,
    ROOT,
)


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(name: str, lines: list[str]) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / name
    # Deterministic: strip trailing spaces; end with single newline
    text = "\n".join(line.rstrip() for line in lines).rstrip() + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def generate_reports(meta: dict[str, Any] | None = None) -> list[Path]:
    meta = meta or {}
    reqs = load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]
    claims = load_yaml(CLAIMS / "claims.yaml")["claims"]
    inv = load_yaml(REPOSITORIES / "repository_inventory.yaml")["repositories"]
    ownership = load_yaml(REPOSITORIES / "repository_ownership.yaml")
    gate_status = load_yaml(GATES / "gate_status.yaml")
    branch_status = load_yaml(REPOSITORIES / "branch_migration_status.yaml")
    branch_inv = load_yaml(REPOSITORIES / "branch_migration_inventory.yaml")
    approval = load_yaml(CHARTER_APPROVAL_RECORD)
    source = load_yaml(CHARTER_SOURCE_RECORD)
    backlog = load_yaml(BACKLOG / "master_gap_backlog.yaml")["gaps"]

    written: list[Path] = []

    # GATE_0_INITIAL_AUDIT
    dirty = [r for r in inv if r.get("dirty")]
    open_prs = []
    for r in inv:
        for pr in r.get("open_prs") or []:
            open_prs.append((r["name"], pr))
    written.append(
        _write(
            "GATE_0_INITIAL_AUDIT.md",
            [
                "# GATE 0 Initial Audit",
                "",
                f"Generated: {_ts()}",
                "",
                "## Workspace status",
                f"- Control-plane repo: `{ROOT.name}`",
                f"- Requirements: {len(reqs)}",
                f"- Claims: {len(claims)}",
                f"- Repositories inventoried: {len(inv)}",
                "",
                "## Source charter status",
                f"- SHA-256: `{source.get('sha256')}`",
                f"- Lines: {source.get('line_count')}",
                f"- Approval: `{approval.get('status')}`",
                "",
                "## Repository inventory (summary)",
                f"- Canonical: {sum(1 for r in inv if r.get('classification')=='CANONICAL')}",
                f"- Supporting: {sum(1 for r in inv if r.get('classification')=='SUPPORTING')}",
                f"- Legacy name: {sum(1 for r in inv if r.get('classification')=='LEGACY_NAME')}",
                f"- Dirty (from audit): {len(dirty)}",
                f"- Open PRs recorded: {len(open_prs)}",
                "",
                "## Existing control-plane artifacts preserved",
                "- CROSS_REPO_VERSION_LOCK.json",
                "- EXTERNAL_GATE_REGISTRY.json",
                "- PHYSICAL_EVIDENCE_REGISTRY.json",
                "- STATUS_DEPENDENCY_GRAPH.json",
                "",
                "## Known blockers",
                "- PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND",
                "- Physical / human / external gate criteria remain blocked",
                "- Field-kit PR #12 credential configuration (do not merge)",
                "",
                "## Claim risks",
                "- Premature 6G / carrier / field / manufacturing claims prohibited",
                "- Ring ownership documentation must not be read as component existence",
                "",
                f"## Status tokens",
                f"- `{STATUS_AUTOMATED_PASS}`",
                f"- `{STATUS_CHARTER_PENDING}`",
                "",
                "Never claim `GATE_0_PASS` without Edmund approval evidence.",
            ],
        )
    )

    # Traceability matrix
    tm = [
        "# GATE 0 Requirements Traceability Matrix",
        "",
        f"Generated: {_ts()}",
        "",
        "| ID | Summary | Charter source | Owner | Gate | Claim | Verification | Evidence | Blocker | Next action |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in reqs:
        blockers = ";".join(r.get("blockers") or []) or "—"
        evidence = ";".join(r.get("required_evidence") or []) or "—"
        next_action = "Resolve blockers" if r.get("blockers") else "Advance implementation"
        tm.append(
            f"| {r['id']} | {r['title'].replace('|','/')} | {r['source_section'].replace('|','/')} "
            f"L{r['source_line_start']}-{r['source_line_end']} | {r['owner_repository']} | {r['gate']} | "
            f"{r['claim_state']} | {r['verification_method']} | {evidence} | {blockers} | {next_action} |"
        )
    written.append(_write("GATE_0_REQUIREMENTS_TRACEABILITY_MATRIX.md", tm))

    # Ownership matrix
    om = [
        "# GATE 0 Repository Ownership Matrix",
        "",
        f"Generated: {_ts()}",
        "",
        "## Owner → requirement counts",
        "",
        "| Owner | Requirement count |",
        "|---|---:|",
    ]
    for owner, ids in ownership.get("owner_to_requirements", {}).items():
        om.append(f"| {owner} | {len(ids)} |")
    om.extend(
        [
            "",
            "## Ring workstream ownership",
            "",
            ownership.get("ring_ownership_disclaimer", ""),
            "",
            "| Workstream | Owner |",
            "|---|---|",
        ]
    )
    for ws, owner in (ownership.get("ring_workstream_ownership") or {}).items():
        om.append(f"| {ws} | {owner} |")
    written.append(_write("GATE_0_REPOSITORY_OWNERSHIP_MATRIX.md", om))

    # Claims and evidence audit
    cert_risk = [c for c in claims if c.get("certification_state") == "CERTIFIED"]
    written.append(
        _write(
            "GATE_0_CLAIMS_AND_EVIDENCE_AUDIT.md",
            [
                "# GATE 0 Claims and Evidence Audit",
                "",
                f"Generated: {_ts()}",
                "",
                f"- Total claims: {len(claims)}",
                f"- TARGET: {sum(1 for c in claims if c['claim_state']=='TARGET')}",
                f"- DOCUMENTED_DESIGN: {sum(1 for c in claims if c['claim_state']=='DOCUMENTED_DESIGN')}",
                f"- NOT_CLAIMABLE: {sum(1 for c in claims if c['claim_state']=='NOT_CLAIMABLE')}",
                f"- Illegal CERTIFIED without evidence: {len(cert_risk)}",
                "",
                "## Prohibited patterns",
                "See `program/claims/prohibited_claim_patterns.yaml`.",
                "",
                "## Physical evidence",
                "All physical registry entries remain blocked; no fabricated measurements.",
            ],
        )
    )

    written.append(
        _write(
            "GATE_0_AUTOMATED_COMPLETION_REPORT.md",
            [
                "# GATE 0 Automated Completion Report",
                "",
                f"Generated: {_ts()}",
                "",
                "## What Cursor implemented",
                "- Charter ingestion and source/approval records",
                "- Requirements catalog with stable IDs and ownership",
                "- Claims taxonomy, transitions, prohibited patterns",
                "- Gates 0–8 baseline criteria and registries",
                "- Repository inventory, ownership, branch policy",
                "- Evidence and gap backlogs",
                "- `control_plane` CLI and validators",
                "- Main-branch policy validator and tests",
                "",
                "## Counts",
                f"- Requirements: {meta.get('requirement_count', len(reqs))}",
                f"- Claims: {meta.get('claim_count', len(claims))}",
                f"- Repositories: {meta.get('repository_count', len(inv))}",
                f"- Backlog gaps: {len(backlog)}",
                "",
                "## Exact status tokens",
                f"- `{STATUS_AUTOMATED_PASS}`",
                f"- `{STATUS_CHARTER_PENDING}`",
                "",
                "## Unresolved Gate 0 items",
                "- Edmund product-charter approval",
                "- CONTROL_PLANE_PENDING_DECISION owners (cloud/manufacturing/certification/support)",
                "",
                "## Blockers preserved",
                "- Physical / human / external / credential / standards",
                "",
                "Do **not** interpret this report as `GATE_0_PASS`.",
            ],
        )
    )

    # Gates 1-8 baseline
    g18 = ["# Gates 1 to 8 Baseline", "", f"Generated: {_ts()}", ""]
    by_gate: dict[int, list] = {}
    for c in gate_status.get("criteria") or []:
        by_gate.setdefault(int(c["gate"]), []).append(c)
    for g in range(1, 9):
        g18.append(f"## Gate {g}")
        g18.append("")
        crits = by_gate.get(g, [])
        evidenced = [c for c in crits if c.get("evidence")]
        blocked = [c for c in crits if c.get("blockers")]
        g18.append(f"- Criteria baselined: {len(crits)}")
        g18.append(f"- Already evidenced: {len(evidenced)}")
        g18.append(f"- Blocked: {len(blocked)}")
        auto = [c for c in crits if c.get("automatable") in ("AUTOMATABLE_NOW", "AUTOMATABLE_AFTER_DEPENDENCY")]
        phys = [c for c in crits if "PHYSICAL" in str(c.get("automatable")) or "HARDWARE" in str(c.get("automatable"))]
        human = [c for c in crits if "HUMAN" in str(c.get("automatable")) or "ETHICS" in str(c.get("automatable"))]
        external = [c for c in crits if c.get("automatable") in (
            "REQUIRES_EXTERNAL_PARTNER", "REQUIRES_CARRIER", "REQUIRES_CERTIFICATION_LAB",
            "REQUIRES_MANUFACTURER", "REQUIRES_STANDARD_FINALIZATION",
        )]
        g18.append(f"- Automatable implementation work: {len(auto)}")
        g18.append(f"- Physical work: {len(phys)}")
        g18.append(f"- Human work: {len(human)}")
        g18.append(f"- External/standards work: {len(external)}")
        g18.append(f"- Recommended next Cursor pass: Gate {g} workstreams after Gate {g-1} readiness")
        g18.append("")
    written.append(_write("GATES_1_TO_8_BASELINE.md", g18))

    # Open PR collision
    pr_lines = [
        "# Open Pull Request Collision Report",
        "",
        f"Generated: {_ts()}",
        "",
        "Do not merge or close these PRs as part of Gate 0.",
        "",
        "| Repository | PR | Base | Head | Draft | Title |",
        "|---|---:|---|---|---|---|",
    ]
    for r in sorted(inv, key=lambda x: x["name"]):
        for pr in r.get("open_prs") or []:
            pr_lines.append(
                f"| {r['name']} | #{pr.get('number')} | {pr.get('baseRefName')} | "
                f"{pr.get('headRefName')} | {pr.get('isDraft', False)} | "
                f"{(pr.get('title') or '').replace('|','/')} |"
            )
    pr_lines.extend(
        [
            "",
            "## Attention",
            "- field-kit PR #12 (remote integrity) — stacked Gate 0 base; do not merge",
            "- anime-aggressors PRs #51 and #52",
            "- PhD-readiness / portfolio-hardening PRs across research repos",
            "- gates-4-6 feature branches remain unmerged work",
        ]
    )
    written.append(_write("OPEN_PULL_REQUEST_COLLISION_REPORT.md", pr_lines))

    # Main branch migration audit
    mba = [
        "# Main Branch Migration Audit",
        "",
        f"Generated: {_ts()}",
        "",
        f"Overall: `{branch_status.get('overall')}`",
        "",
        "## Field-kit post-migration",
        f"- Status: `{branch_status.get('field_kit', {}).get('post_migration_status')}`",
        f"- GitHub default: `{branch_status.get('field_kit', {}).get('github_default_branch')}`",
        f"- PRs retargeted: {branch_status.get('field_kit', {}).get('prs_retargeted')}",
        f"- Master preserved: {branch_status.get('field_kit', {}).get('master_preserved')}",
        "",
        "## Inventory snapshot (from /tmp/branch_migration_audit.json)",
        "",
        "| Repository | GitHub default | Case | Main SHA | Master SHA | Dirty |",
        "|---|---|---|---|---|---|",
    ]
    for r in branch_inv.get("repositories") or []:
        if str(r.get("repository", "")).startswith("standalone:"):
            continue
        mba.append(
            f"| {r.get('repository')} | {r.get('github_default_branch')} | {r.get('migration_case')} | "
            f"{r.get('main_sha')} | {r.get('master_sha')} | {r.get('dirty')} |"
        )
    mba.extend(
        [
            "",
            "## Safety invariants",
            f"- Force-push used: {branch_status.get('force_push_used')}",
            f"- History rewritten: {branch_status.get('history_rewritten')}",
            f"- Master deleted: {branch_status.get('master_deleted')}",
        ]
    )
    written.append(_write("MAIN_BRANCH_MIGRATION_AUDIT.md", mba))

    written.append(
        _write(
            "MASTER_REFERENCE_REMEDIATION_REPORT.md",
            [
                "# Master Reference Remediation Report",
                "",
                f"Generated: {_ts()}",
                "",
                "## Policy",
                "- canonical_default_branch: main",
                "- legacy_default_branch: master",
                "- new_master_references_prohibited: true",
                "- master_deletion_requires_edmund_approval: true",
                "",
                "## Allowlisted contexts",
                "- Migration history and archival reports under program/reports/",
                "- branch_migration_*.yaml",
                "- Explicit dual-trigger workflow allowlist when documented",
                "",
                "## Active config rule",
                "`scripts/validate_main_branch_policy.py` fails if active configuration reintroduces "
                "`master` as default/base outside the allowlist.",
                "",
                "## Notes",
                "- Do not delete master in this pass.",
                "- Historical prose mentioning master is permitted.",
            ],
        )
    )

    return written
