"""Aggregate Gate 1 results, status tokens, and reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gate1 import (
    STATUS_AUTOMATED_PASS,
    STATUS_AUTOMATED_PARTIAL,
    STATUS_FAIL,
    STATUS_GATE_1_PASS,
    STATUS_PHYSICAL_PENDING,
    STATUS_SOFTWARE_READY,
)
from gate1.orchestrator import (
    ACCEPTED,
    COLLISION_AUDIT,
    DEFAULT_REPOS_ROOT,
    PENDING,
    REPORTS,
    REPO_LOCK,
    REPO_ROOT,
    REQUIRED_PHYSICAL_WORKSTREAMS,
)
from gate1.orchestrator.evidence_collector import (
    accepted_physical_workstreams,
    list_bucket,
    tool_versions,
    utc_now,
)
from gate1.orchestrator.evidence_validator import physical_evidence_complete


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_report(name: str, lines: list[str]) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / name
    path.write_text("\n".join(line.rstrip() for line in lines).rstrip() + "\n", encoding="utf-8")
    return path


def compute_status(run_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    phys = accepted_physical_workstreams()
    physical_complete = physical_evidence_complete(phys)
    software_ok = False
    failures: list[str] = ["no_run_yet"]
    if run_payload is not None:
        software_ok = bool(run_payload.get("ok"))
        failures = list(run_payload.get("software_failures") or [])
        if run_payload.get("contract_issues"):
            software_ok = False
            failures.append("contracts")

    if run_payload is None:
        overall = STATUS_AUTOMATED_PARTIAL
        secondary = STATUS_PHYSICAL_PENDING
        criterion_status = "NOT_RUN"
    elif not software_ok:
        overall = STATUS_FAIL
        secondary = STATUS_PHYSICAL_PENDING
        criterion_status = "SOFTWARE_FAIL"
    elif physical_complete:
        overall = STATUS_GATE_1_PASS
        secondary = STATUS_SOFTWARE_READY
        criterion_status = STATUS_GATE_1_PASS
    else:
        overall = STATUS_AUTOMATED_PASS
        secondary = STATUS_PHYSICAL_PENDING
        criterion_status = STATUS_SOFTWARE_READY

    # Explicit rule: never GATE_1_PASS without physical
    if overall == STATUS_GATE_1_PASS and not physical_complete:
        overall = STATUS_AUTOMATED_PASS
        criterion_status = STATUS_SOFTWARE_READY

    g1_criteria = []
    mapping = {
        "G1-C1": "boot",
        "G1-C2": "ring-auth",
        "G1-C3": "dock",
        "G1-C4": "ai-runtime",
        "G1-C5": "games",
    }
    for cid, ws in mapping.items():
        if run_payload is None:
            status = "NOT_RUN/PHYSICAL_EVIDENCE_PENDING"
        elif not software_ok:
            status = "SOFTWARE_FAIL"
        elif ws in phys:
            status = "PHYSICAL_EVIDENCE_ACCEPTED"
        else:
            status = f"{STATUS_SOFTWARE_READY}/{STATUS_PHYSICAL_PENDING}"
        g1_criteria.append({"criterion_id": cid, "workstream": ws, "status": status})

    return {
        "overall": overall,
        "secondary": secondary,
        "software_ok": software_ok,
        "software_failures": failures,
        "physical_workstreams_accepted": sorted(phys),
        "physical_complete": physical_complete,
        "prohibited_without_physical": STATUS_GATE_1_PASS,
        "criterion_status_token": criterion_status,
        "gate1_criteria": g1_criteria,
        "pending_count": len(list_bucket(PENDING)),
        "accepted_count": len(list_bucket(ACCEPTED)),
        "tool_versions": tool_versions(),
        "collected_at_utc": utc_now(),
    }


def equipment_inventory(repos_root: Path | None = None) -> dict[str, Any]:
    """Inventory without assuming equipment exists."""
    root = repos_root or DEFAULT_REPOS_ROOT
    items = [
        ("representative_boot_hardware", "MISSING_ASSUMED", "REQUIRES_LOCAL_HARDWARE"),
        ("ring_prototype", "MISSING_ASSUMED", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("dock_station", "MISSING_ASSUMED", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("on_device_ai_runtime_target", "MISSING_ASSUMED", "REQUIRES_LOCAL_HARDWARE"),
        ("game_target_device", "MISSING_ASSUMED", "REQUIRES_LOCAL_HARDWARE"),
    ]
    return {
        "command": "python -m gate1.orchestrator.cli status --equipment-inventory",
        "repos_root": str(root),
        "assumption": "Equipment existence is NEVER assumed.",
        "items": [
            {"name": n, "status": s, "blocker_class": b} for n, s, b in items
        ],
        "note": "Operator must replace MISSING_ASSUMED with PRESENT only after local inspection.",
    }


def generate_reports(run_payload: dict[str, Any] | None, status: dict[str, Any]) -> list[Path]:
    written: list[Path] = []
    discovery = (run_payload or {}).get("discovery") or {}
    components = (run_payload or {}).get("components") or {}

    written.append(
        _write_report(
            "GATE_1_INITIAL_AUDIT.md",
            [
                "# GATE 1 Initial Audit",
                "",
                f"Generated: {_ts()}",
                "",
                "## Scope",
                "- Integrated development platform: boot, ring-auth, dock, local AI, game core loops",
                f"- Control-plane repo: `{REPO_ROOT.name}`",
                f"- Sibling repos discovered: {discovery.get('sibling_count', 'n/a')}",
                f"- repo-lock present: {discovery.get('repo_lock_present', REPO_LOCK.exists())}",
                "",
                "## Status tokens",
                f"- overall: `{status['overall']}`",
                f"- secondary: `{status['secondary']}`",
                f"- prohibited without physical: `{STATUS_GATE_1_PASS}`",
                "",
                "## Workstream snapshot",
            ]
            + [
                f"- {cid}: `{row['status']}`"
                for row in status["gate1_criteria"]
                for cid in [row["criterion_id"]]
            ]
            + [
                "",
                "## Non-claims",
                "- No physical boot/dock/ring/AI/game completion claimed without accepted physical evidence.",
            ],
        )
    )

    # Collision report from /tmp/gate1_collision_audit.json
    collision_lines = [
        "# GATE 1 Open PR Collision Report",
        "",
        f"Generated: {_ts()}",
        "",
        "Do not merge or close unrelated open PRs as part of Gate 1 automation.",
        "",
    ]
    if COLLISION_AUDIT.exists():
        data = json.loads(COLLISION_AUDIT.read_text(encoding="utf-8"))
        collision_lines.append(f"Source: `{COLLISION_AUDIT}` (generated_at={data.get('generated_at')})")
        collision_lines.extend(
            [
                "",
                "| Repository | Access | Local branch | Dirty | Open PRs |",
                "|---|---|---|---|---|",
            ]
        )
        for row in data.get("rows") or []:
            prs = row.get("open_prs") or []
            pr_txt = "; ".join(
                f"#{p.get('number')} {p.get('headRefName')}→{p.get('baseRefName')}" for p in prs
            ) or "—"
            collision_lines.append(
                f"| {row.get('repo')} | {row.get('access')} | {row.get('local_branch')} | "
                f"{row.get('dirty')} | {pr_txt.replace('|', '/')} |"
            )
        collision_lines.extend(["", "## PR details", ""])
        for row in data.get("rows") or []:
            for pr in row.get("open_prs") or []:
                collision_lines.append(
                    f"- `{row.get('repo')}` PR #{pr.get('number')}: {pr.get('title')} "
                    f"({pr.get('url')}) draft={pr.get('isDraft')}"
                )
    else:
        collision_lines.append("Collision audit file `/tmp/gate1_collision_audit.json` not present.")
    written.append(_write_report("GATE_1_OPEN_PR_COLLISION_REPORT.md", collision_lines))

    matrix = [
        "# GATE 1 Implementation Matrix",
        "",
        f"Generated: {_ts()}",
        "",
        "| Workstream | Available | Software OK | Physical OK | Evidence class |",
        "|---|---|---|---|---|",
    ]
    for ws, result in components.items():
        matrix.append(
            f"| {ws} | {result.get('available')} | {result.get('software_ok')} | "
            f"{result.get('physical_ok')} | {result.get('evidence_class')} |"
        )
    if not components:
        matrix.append("| (no run yet) | — | — | — | — |")
    written.append(_write_report("GATE_1_IMPLEMENTATION_MATRIX.md", matrix))

    written.append(
        _write_report(
            "GATE_1_AUTOMATED_COMPLETION_REPORT.md",
            [
                "# GATE 1 Automated Completion Report",
                "",
                f"Generated: {_ts()}",
                "",
                "## Exact status tokens",
                f"- `{status['overall']}`",
                f"- `{status['secondary']}`",
                f"- criterion representation: `{STATUS_SOFTWARE_READY}` / `{STATUS_PHYSICAL_PENDING}`",
                "",
                "## Software slice",
                f"- software_ok: {status['software_ok']}",
                f"- failures: {', '.join(status['software_failures']) or 'none'}",
                f"- pending evidence files: {status['pending_count']}",
                f"- accepted evidence files: {status['accepted_count']}",
                "",
                "## Physical",
                f"- accepted workstreams: {', '.join(status['physical_workstreams_accepted']) or 'none'}",
                f"- physical_complete: {status['physical_complete']}",
                "",
                "## Interpretation",
                f"- `{STATUS_AUTOMATED_PASS}` means automatable software slices passed while physical evidence remains pending.",
                f"- Do **not** interpret this as `{STATUS_GATE_1_PASS}`.",
                f"- `{STATUS_GATE_1_PASS}` requires accepted physical evidence for: "
                + ", ".join(REQUIRED_PHYSICAL_WORKSTREAMS),
            ],
        )
    )

    inv = equipment_inventory()
    packet = [
        "# GATE 1 Physical Action Packet",
        "",
        f"Generated: {_ts()}",
        "",
        "## Equipment inventory command",
        "",
        "```bash",
        inv["command"],
        "```",
        "",
        f"**Assumption:** {inv['assumption']}",
        "",
        "## Inventory (default — does not claim equipment exists)",
        "",
        "| Item | Status | Blocker |",
        "|---|---|---|",
    ]
    for item in inv["items"]:
        packet.append(f"| {item['name']} | {item['status']} | {item['blocker_class']} |")
    packet.extend(
        [
            "",
            "## Exact steps",
            "",
            "### A. Boot (G1-C1)",
            "1. Run equipment inventory; confirm representative hardware is PRESENT (do not assume).",
            "2. Image/boot candidate per `gunnchos-device-os` boot_readiness docs.",
            "3. Capture device identity, boot duration, service health, storage, display/input, network.",
            "4. Write physical evidence JSON (`evidence_class=physical`, `claim_level=PHYSICAL_BOOT`).",
            "5. `python -m gate1.orchestrator.cli ingest-evidence <path>` then operator-move to `accepted/`.",
            "",
            "### B. Ring authenticated input (G1-C2)",
            "1. Inventory ring prototype; if MISSING, stop — do not fabricate.",
            "2. Pair ring using documented auth path (hardware-industrial-design / edge-io / device-os).",
            "3. Capture authenticated frame with anti-replay nonce and payload digest.",
            "4. Ingest physical evidence (`claim_level=PHYSICAL_RING`).",
            "",
            "### C. Dock continuity (G1-C3)",
            "1. Inventory dock station; if MISSING, stop.",
            "2. Dock device; record power negotiation, display handoff, session continuity.",
            "3. Ingest physical evidence (`claim_level=PHYSICAL_DOCK`).",
            "",
            "### D. Local AI runtime (G1-C4)",
            "1. Inventory on-device AI target; if MISSING, stop.",
            "2. Start gunnchAI3k local-only mode; verify network egress denied.",
            "3. Capture runtime health + version; ingest (`claim_level=PHYSICAL_AI_DEVICE`).",
            "",
            "### E. Game core loops (G1-C5)",
            "For each game — beatlink-party, archive-of-life-artifact-world, pedestrian-pursuit, anime-aggressors:",
            "1. Confirm target device PRESENT via inventory.",
            "2. Launch software harness/runtime available in that repo.",
            "3. Complete one core loop; record steps_completed.",
            "4. Ingest physical evidence (`claim_level=PHYSICAL_GAME_DEVICE`, workstream=games).",
            "",
            "## Acceptance",
            "- Only files under `gate1/evidence/accepted/` with `evidence_class=physical` upgrade physical claims.",
            "- Simulated/software evidence must remain classified as such.",
        ]
    )
    written.append(_write_report("GATE_1_PHYSICAL_ACTION_PACKET.md", packet))

    written.append(
        _write_report(
            "GATE_1_EVIDENCE_ACCEPTANCE_REPORT.md",
            [
                "# GATE 1 Evidence Acceptance Report",
                "",
                f"Generated: {_ts()}",
                "",
                f"- pending: {status['pending_count']}",
                f"- accepted: {status['accepted_count']}",
                f"- physical workstreams accepted: {', '.join(status['physical_workstreams_accepted']) or 'none'}",
                "",
                "## Rules",
                "- Hash must match `artifact_sha256` (content digest).",
                "- Physical claim levels require `evidence_class=physical`.",
                "- Unsupported upgrades are refused and moved to `rejected/`.",
            ],
        )
    )

    for name, title, body in [
        (
            "GATE_1_SECURITY_REVIEW.md",
            "GATE 1 Security Review",
            [
                "- Authenticated input requires anti-replay nonce and payload digest.",
                "- Local AI runtime must default to local_only with network egress denied.",
                "- Evidence tampering detected via artifact hash verification.",
                "- No secrets are written into evidence JSON by the orchestrator.",
            ],
        ),
        (
            "GATE_1_PRIVACY_REVIEW.md",
            "GATE 1 Privacy Review",
            [
                "- Prefer device_id software labels over personal identifiers.",
                "- Ring/AI software probes use fixtures; no biometric raw capture claimed.",
                "- Physical evidence packets must avoid unnecessary PII.",
            ],
        ),
        (
            "GATE_1_SAFETY_REVIEW.md",
            "GATE 1 Safety Review",
            [
                "- Physical steps require operator presence; automation does not drive actuators.",
                "- Dock/power steps must abort if equipment inventory reports MISSING.",
                "- No destructive flash/update commands are invoked by Gate 1 orchestrator.",
            ],
        ),
        (
            "GATE_1_FAILURE_REPRODUCTION.md",
            "GATE 1 Failure Reproduction",
            [
                "1. Remove or break a sibling game repo path and re-run `python -m gate1.orchestrator.cli run`.",
                "2. Expect nonzero exit and `GATE_1_SOFTWARE_FAIL`.",
                "3. Tamper a pending JSON `artifact_sha256` and run `validate-evidence` — expect rejection.",
                "4. Attempt claim_level=PHYSICAL_BOOT with evidence_class=software — expect CLAIM_UPGRADE_REFUSED.",
            ],
        ),
        (
            "GATE_1_NEXT_ACTIONS.md",
            "GATE 1 Next Actions",
            [
                "1. Keep Gate 0 approval record APPROVED; do not regress to pending.",
                "2. Execute physical action packet per workstream when equipment is PRESENT.",
                "3. Accept physical evidence into `gate1/evidence/accepted/`.",
                "4. Only then evaluate `GATE_1_PASS`.",
                "5. Proceed to Gate 2 only after Gate 1 physical closure or explicit waiver by Edmund.",
            ],
        ),
    ]:
        written.append(
            _write_report(
                name,
                [f"# {title}", "", f"Generated: {_ts()}", ""] + body,
            )
        )

    # Cross-repo version lock snapshot
    lock_lines = [
        "# GATE 1 Cross-Repo Version Lock",
        "",
        f"Generated: {_ts()}",
        "",
        f"- integration/repo-lock.json present: {REPO_LOCK.exists()}",
    ]
    if REPO_LOCK.exists():
        lock = json.loads(REPO_LOCK.read_text(encoding="utf-8"))
        lock_lines.append(f"- schema_version: {lock.get('schema_version')}")
        lock_lines.append(f"- locked_at: {lock.get('locked_at')}")
        lock_lines.append("")
        lock_lines.append("| Component | Commit | Branch | Required |")
        lock_lines.append("|---|---|---|---|")
        for name, comp in (lock.get("components") or {}).items():
            lock_lines.append(
                f"| {name} | `{comp.get('commit')}` | {comp.get('branch') or comp.get('checked_out_branch')} | "
                f"{comp.get('required')} |"
            )
    else:
        lock_lines.append("- WARNING: repo-lock missing; discovery still proceeds from sibling directories.")
    written.append(_write_report("GATE_1_CROSS_REPO_VERSION_LOCK.md", lock_lines))

    # Persist status snapshot under runs/ (not evidence acceptance)
    from gate1.orchestrator.evidence_collector import write_run

    write_run(f"status_{status['collected_at_utc'].replace(':', '')}.json", status)
    return written
