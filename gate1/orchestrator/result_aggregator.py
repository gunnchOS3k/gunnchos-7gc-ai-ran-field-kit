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

_report_root: Path | None = None
_reports_no_write: bool = False


def configure_report_writes(*, report_dir: Path | None = None, no_write: bool = False) -> None:
    global _report_root, _reports_no_write
    _report_root = report_dir
    _reports_no_write = no_write


def reset_report_writes() -> None:
    configure_report_writes(report_dir=None, no_write=False)


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_report(name: str, lines: list[str]) -> Path | None:
    if _reports_no_write:
        return None
    root = _report_root or REPORTS
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
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
        "command": "python -m gate1.operator.cli inventory",
        "legacy_command": "python -m gate1.orchestrator.cli status --equipment-inventory",
        "repos_root": str(root),
        "assumption": "Equipment existence is NEVER assumed.",
        "items": [{"name": n, "status": s, "blocker_class": b} for n, s, b in items],
        "note": "Operator must replace MISSING_ASSUMED with PRESENT_CONFIRMED only after local inspection.",
    }


def _physical_action_packet_lines(inv: dict[str, Any]) -> list[str]:
    """Operator-grade runbook body (also maintained as the committed packet)."""
    lines = [
        "# GATE 1 Physical Action Packet",
        "",
        f"Generated: {_ts()}",
        "",
        "## Status posture",
        "",
        "- Local automation may report `GATE_1_LOCAL_AUTOMATION_PASS` / `GATE_1_AUTOMATED_PASS`.",
        "- Remote CI remains `GATE_1_REMOTE_CI_PENDING` until green on `main`.",
        "- Physical remains `GATE_1_PHYSICAL_EVIDENCE_PENDING` until Edmund accepts a physical bundle.",
        "- `GATE_1_PASS` is **prohibited** without accepted physical evidence.",
        "",
        "## Equipment inventory commands",
        "",
        "```bash",
        "# Preferred — operator inventory (never invents hardware)",
        "python -m gate1.operator.cli inventory",
        "python -m gate1.operator.cli plan",
        "",
        "# Legacy soft inventory (defaults to MISSING_ASSUMED)",
        inv["legacy_command"],
        "```",
        "",
        f"**Assumption:** {inv['assumption']}",
        "",
        "## Detection logic (classification tokens)",
        "",
        "| Token | Meaning |",
        "|---|---|",
        "| `PRESENT_CONFIRMED` | Tooling observed the device/interface on this host |",
        "| `MISSING` | Tooling ran; target not observed |",
        "| `MISSING_ASSUMED` | Soft default before operator inventory (do not treat as confirmed) |",
        "| `TOOLCHAIN_MISSING` | Required probe tool (adb/system_profiler/…) unavailable |",
        "| `UNSUPPORTED_PLATFORM` | Host OS not covered by inventory adapter |",
        "| `PERMISSION_DENIED` | Tooling present but OS blocked the probe |",
        "| `INDETERMINATE` | Partial/ambiguous observation; do not claim PRESENT |",
        "",
        "## Inventory (default — does not claim equipment exists)",
        "",
        "| Item | Status | Blocker |",
        "|---|---|---|",
    ]
    for item in inv["items"]:
        lines.append(f"| {item['name']} | {item['status']} | {item['blocker_class']} |")
    lines.extend(
        [
            "",
            "## Session workflow (exact commands)",
            "",
            "```bash",
            "# 1) Inventory host + USB/ADB surfaces",
            "python -m gate1.operator.cli inventory --json > /tmp/gate1_inventory.json",
            "",
            "# 2) Build workstream plan from inventory + requirements",
            "python -m gate1.operator.cli plan --inventory /tmp/gate1_inventory.json",
            "",
            "# 3) Start evidence session (writes under gate1/evidence/pending/sessions/…)",
            "python -m gate1.operator.cli start-session --workstream boot",
            "",
            "# 4) Run checklist item(s); capture only observed facts",
            "python -m gate1.operator.cli run-check --session <session_id> --check boot_identity",
            "",
            "# 5) Finalize session bundle (redacted)",
            "python -m gate1.operator.cli finalize-session --session <session_id>",
            "",
            "# 6) Validate bundle schema/hashes (does NOT accept)",
            "python -m gate1.operator.cli validate-bundle --bundle <bundle_path>",
            "",
            "# 7) Accept ONLY with explicit Edmund decision record",
            "python -m gate1.operator.cli accept-bundle \\",
            "  --bundle <bundle_path> \\",
            "  --decision-record gate1/operator/schemas/examples/edmund_decision_record.example.json",
            "",
            "# 8) Final status tokens",
            "python -m gate1.operator.cli final-status",
            "```",
            "",
            "## Exact workstream steps",
            "",
            "### A. Boot (G1-C1)",
            "1. Run operator inventory; require `PRESENT_CONFIRMED` for representative boot hardware.",
            "2. If `MISSING` / `TOOLCHAIN_MISSING` / `INDETERMINATE` — stop; record blocker; do not fabricate.",
            "3. Image/boot candidate per `gunnchos-device-os` boot_readiness docs (operator-driven).",
            "4. Capture device identity, boot duration, service health, storage, display/input, network.",
            "5. Write physical evidence JSON (`evidence_class=physical`, `claim_level=PHYSICAL_BOOT`).",
            "6. Validate bundle; accept only via `accept-bundle` with Edmund decision record.",
            "",
            "### B. Ring authenticated input (G1-C2)",
            "1. Inventory ring prototype; if not `PRESENT_CONFIRMED`, stop.",
            "2. Pair ring using documented auth path (hardware-industrial-design / edge-io / device-os).",
            "3. Capture authenticated frame with anti-replay nonce and payload digest.",
            "4. Ingest/finalize physical evidence (`claim_level=PHYSICAL_RING`).",
            "",
            "### C. Dock continuity (G1-C3)",
            "1. Inventory dock station; if not `PRESENT_CONFIRMED`, stop.",
            "2. Dock device; record power negotiation, display handoff, session continuity.",
            "3. Finalize physical evidence (`claim_level=PHYSICAL_DOCK`).",
            "",
            "### D. Local AI runtime (G1-C4)",
            "1. Inventory on-device AI target; if not `PRESENT_CONFIRMED`, stop.",
            "2. Start gunnchAI3k local-only mode; verify network egress denied.",
            "3. Capture runtime health + version; finalize (`claim_level=PHYSICAL_AI_DEVICE`).",
            "",
            "### E. Game core loops (G1-C5)",
            "For each game — beatlink-party, archive-of-life-artifact-world, pedestrian-pursuit, anime-aggressors:",
            "1. Confirm target device `PRESENT_CONFIRMED` via inventory.",
            "2. Launch software harness/runtime available in that repo.",
            "3. Complete one core loop; record steps_completed.",
            "4. Finalize physical evidence (`claim_level=PHYSICAL_GAME_DEVICE`, workstream=games).",
            "",
            "## Pass / fail criteria",
            "",
            "| Outcome | Condition |",
            "|---|---|",
            "| PASS (workstream) | Bundle validates; evidence_class=physical; Edmund decision ACCEPT; file under accepted/ |",
            "| FAIL (workstream) | Schema/hash fail, claim upgrade refused, or equipment not PRESENT_CONFIRMED |",
            "| BLOCKED | Toolchain missing / permission denied / acquisition required |",
            "| Gate PASS | All of boot, ring-auth, dock, ai-runtime, games accepted physically |",
            "",
            "## Recovery",
            "",
            "1. `TOOLCHAIN_MISSING` — install probe tool (Xcode CLI / adb / …), re-run inventory.",
            "2. `PERMISSION_DENIED` — grant OS permission, re-run the same check; do not invent results.",
            "3. Hash mismatch — discard bundle; re-finalize; never hand-edit `artifact_sha256`.",
            "4. Claim upgrade refused — keep software classification; start a new physical session only with real hardware.",
            "5. Dirty git from runtime outputs — evidence dirs are gitignored; use `--no-write` / `--output-dir` for dry runs.",
            "",
            "## Schemas",
            "",
            "- `gate1/operator/schemas/inventory_item.schema.json`",
            "- `gate1/operator/schemas/evidence_session.schema.json`",
            "- `gate1/operator/schemas/evidence_bundle.schema.json`",
            "- `gate1/operator/schemas/edmund_decision_record.schema.json`",
            "- `gate1/contracts/evidence_event.schema.json`",
            "",
            "## Acceptance authority",
            "",
            "- Only files under `gate1/evidence/accepted/` with `evidence_class=physical` upgrade physical claims.",
            "- Simulated/software evidence must remain classified as such.",
            "- `accept-bundle` **requires** an explicit Edmund decision record; automation never auto-accepts.",
            "- No equipment assumptions: absence of evidence is `MISSING`, not `PRESENT`.",
        ]
    )
    return lines


def generate_reports(
    run_payload: dict[str, Any] | None,
    status: dict[str, Any],
    *,
    output_dir: Path | None = None,
    no_write: bool = False,
) -> list[Path]:
    written: list[Path] = []
    discovery = (run_payload or {}).get("discovery") or {}
    components = (run_payload or {}).get("components") or {}
    report_dir = (output_dir / "reports") if output_dir is not None else None
    configure_report_writes(report_dir=report_dir, no_write=no_write)
    from gate1.orchestrator.evidence_collector import configure_write_paths, reset_write_paths, write_run

    if output_dir is not None:
        configure_write_paths(
            pending=output_dir / "pending",
            runs=output_dir / "runs",
            no_write=no_write,
        )
    else:
        configure_write_paths(no_write=no_write)

    def _keep(path: Path | None) -> None:
        if path is not None:
            written.append(path)

    try:
        _keep(
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
                    f"- {row['criterion_id']}: `{row['status']}`" for row in status["gate1_criteria"]
                ]
                + [
                    "",
                    "## Non-claims",
                    "- No physical boot/dock/ring/AI/game completion claimed without accepted physical evidence.",
                ],
            )
        )

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
            collision_lines.append(
                f"Source: `{COLLISION_AUDIT}` (generated_at={data.get('generated_at')})"
            )
            collision_lines.extend(
                [
                    "",
                    "| Repository | Access | Local branch | Dirty | Open PRs |",
                    "|---|---|---|---|---|",
                ]
            )
            for row in data.get("rows") or []:
                prs = row.get("open_prs") or []
                pr_txt = (
                    "; ".join(
                        f"#{p.get('number')} {p.get('headRefName')}→{p.get('baseRefName')}" for p in prs
                    )
                    or "—"
                )
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
            collision_lines.append(
                "Collision audit file `/tmp/gate1_collision_audit.json` not present."
            )
        _keep(_write_report("GATE_1_OPEN_PR_COLLISION_REPORT.md", collision_lines))

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
        _keep(_write_report("GATE_1_IMPLEMENTATION_MATRIX.md", matrix))

        _keep(
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
        _keep(_write_report("GATE_1_PHYSICAL_ACTION_PACKET.md", _physical_action_packet_lines(inv)))

        _keep(
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
                    "- Operator `accept-bundle` requires an explicit Edmund decision record.",
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
                    "- Operator redaction strips serials/MACs/emails before finalize when configured.",
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
                    "5. Call `accept-bundle` without Edmund decision record — expect refusal.",
                ],
            ),
            (
                "GATE_1_NEXT_ACTIONS.md",
                "GATE 1 Next Actions",
                [
                    "1. Keep Gate 0 approval record APPROVED; do not regress to pending.",
                    "2. Execute physical action packet per workstream when equipment is PRESENT_CONFIRMED.",
                    "3. Accept physical evidence via operator `accept-bundle` with Edmund decision record.",
                    "4. Only then evaluate `GATE_1_PASS`.",
                    "5. Proceed to Gate 2 only after Gate 1 physical closure or explicit waiver by Edmund.",
                ],
            ),
        ]:
            _keep(_write_report(name, [f"# {title}", "", f"Generated: {_ts()}", ""] + body))

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
            lock_lines.append(
                "- WARNING: repo-lock missing; discovery still proceeds from sibling directories."
            )
        _keep(_write_report("GATE_1_CROSS_REPO_VERSION_LOCK.md", lock_lines))

        write_run(f"status_{status['collected_at_utc'].replace(':', '')}.json", status)
        return written
    finally:
        reset_write_paths()
        reset_report_writes()
