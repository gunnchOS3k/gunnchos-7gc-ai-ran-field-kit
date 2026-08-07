# GATE 1 Physical Action Packet

Generated: 2026-08-07T20:52:15Z

## Status posture

- Local automation may report `GATE_1_LOCAL_AUTOMATION_PASS` / `GATE_1_AUTOMATED_PASS`.
- Remote CI remains `GATE_1_REMOTE_CI_PENDING` until green on `main`.
- Physical remains `GATE_1_PHYSICAL_EVIDENCE_PENDING` until Edmund accepts a physical bundle.
- `GATE_1_PASS` is **prohibited** without accepted physical evidence.

## Equipment inventory commands

```bash
# Preferred — operator inventory (never invents hardware)
python -m gate1.operator.cli inventory
python -m gate1.operator.cli plan

# Legacy soft inventory (defaults to MISSING_ASSUMED)
python -m gate1.orchestrator.cli status --equipment-inventory
```

**Assumption:** Equipment existence is NEVER assumed.

## Detection logic (classification tokens)

| Token | Meaning |
|---|---|
| `PRESENT_CONFIRMED` | Tooling observed the device/interface on this host |
| `MISSING` | Tooling ran; target not observed |
| `MISSING_ASSUMED` | Soft default before operator inventory (do not treat as confirmed) |
| `TOOLCHAIN_MISSING` | Required probe tool (adb/system_profiler/…) unavailable |
| `UNSUPPORTED_PLATFORM` | Host OS not covered by inventory adapter |
| `PERMISSION_DENIED` | Tooling present but OS blocked the probe |
| `INDETERMINATE` | Partial/ambiguous observation; do not claim PRESENT |

## Inventory (default — does not claim equipment exists)

| Item | Status | Blocker |
|---|---|---|
| representative_boot_hardware | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |
| ring_prototype | MISSING_ASSUMED | REQUIRES_PHYSICAL_PROTOTYPE |
| dock_station | MISSING_ASSUMED | REQUIRES_PHYSICAL_PROTOTYPE |
| on_device_ai_runtime_target | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |
| game_target_device | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |

## Session workflow (exact commands)

```bash
# 1) Inventory host + USB/ADB surfaces
python -m gate1.operator.cli inventory --json > /tmp/gate1_inventory.json

# 2) Build workstream plan from inventory + requirements
python -m gate1.operator.cli plan --inventory /tmp/gate1_inventory.json

# 3) Start evidence session (writes under gate1/evidence/pending/sessions/…)
python -m gate1.operator.cli start-session --workstream boot

# 4) Run checklist item(s); capture only observed facts
python -m gate1.operator.cli run-check --session <session_id> --check boot_identity

# 5) Finalize session bundle (redacted)
python -m gate1.operator.cli finalize-session --session <session_id>

# 6) Validate bundle schema/hashes (does NOT accept)
python -m gate1.operator.cli validate-bundle --bundle <bundle_path>

# 7) Accept ONLY with explicit Edmund decision record
python -m gate1.operator.cli accept-bundle \
  --bundle <bundle_path> \
  --decision-record gate1/operator/schemas/examples/edmund_decision_record.example.json

# 8) Final status tokens
python -m gate1.operator.cli final-status
```

## Exact workstream steps

### A. Boot (G1-C1)
1. Run operator inventory; require `PRESENT_CONFIRMED` for representative boot hardware.
2. If `MISSING` / `TOOLCHAIN_MISSING` / `INDETERMINATE` — stop; record blocker; do not fabricate.
3. Image/boot candidate per `gunnchos-device-os` boot_readiness docs (operator-driven).
4. Capture device identity, boot duration, service health, storage, display/input, network.
5. Write physical evidence JSON (`evidence_class=physical`, `claim_level=PHYSICAL_BOOT`).
6. Validate bundle; accept only via `accept-bundle` with Edmund decision record.

### B. Ring authenticated input (G1-C2)
1. Inventory ring prototype; if not `PRESENT_CONFIRMED`, stop.
2. Pair ring using documented auth path (hardware-industrial-design / edge-io / device-os).
3. Capture authenticated frame with anti-replay nonce and payload digest.
4. Ingest/finalize physical evidence (`claim_level=PHYSICAL_RING`).

### C. Dock continuity (G1-C3)
1. Inventory dock station; if not `PRESENT_CONFIRMED`, stop.
2. Dock device; record power negotiation, display handoff, session continuity.
3. Finalize physical evidence (`claim_level=PHYSICAL_DOCK`).

### D. Local AI runtime (G1-C4)
1. Inventory on-device AI target; if not `PRESENT_CONFIRMED`, stop.
2. Start gunnchAI3k local-only mode; verify network egress denied.
3. Capture runtime health + version; finalize (`claim_level=PHYSICAL_AI_DEVICE`).

### E. Game core loops (G1-C5)
For each game — beatlink-party, archive-of-life-artifact-world, pedestrian-pursuit, anime-aggressors:
1. Confirm target device `PRESENT_CONFIRMED` via inventory.
2. Launch software harness/runtime available in that repo.
3. Complete one core loop; record steps_completed.
4. Finalize physical evidence (`claim_level=PHYSICAL_GAME_DEVICE`, workstream=games).

## Pass / fail criteria

| Outcome | Condition |
|---|---|
| PASS (workstream) | Bundle validates; evidence_class=physical; Edmund decision ACCEPT; file under accepted/ |
| FAIL (workstream) | Schema/hash fail, claim upgrade refused, or equipment not PRESENT_CONFIRMED |
| BLOCKED | Toolchain missing / permission denied / acquisition required |
| Gate PASS | All of boot, ring-auth, dock, ai-runtime, games accepted physically |

## Recovery

1. `TOOLCHAIN_MISSING` — install probe tool (Xcode CLI / adb / …), re-run inventory.
2. `PERMISSION_DENIED` — grant OS permission, re-run the same check; do not invent results.
3. Hash mismatch — discard bundle; re-finalize; never hand-edit `artifact_sha256`.
4. Claim upgrade refused — keep software classification; start a new physical session only with real hardware.
5. Dirty git from runtime outputs — evidence dirs are gitignored; use `--no-write` / `--output-dir` for dry runs.

## Schemas

- `gate1/operator/schemas/inventory_item.schema.json`
- `gate1/operator/schemas/evidence_session.schema.json`
- `gate1/operator/schemas/evidence_bundle.schema.json`
- `gate1/operator/schemas/edmund_decision_record.schema.json`
- `gate1/contracts/evidence_event.schema.json`

## Acceptance authority

- Only files under `gate1/evidence/accepted/` with `evidence_class=physical` upgrade physical claims.
- Simulated/software evidence must remain classified as such.
- `accept-bundle` **requires** an explicit Edmund decision record; automation never auto-accepts.
- No equipment assumptions: absence of evidence is `MISSING`, not `PRESENT`.
