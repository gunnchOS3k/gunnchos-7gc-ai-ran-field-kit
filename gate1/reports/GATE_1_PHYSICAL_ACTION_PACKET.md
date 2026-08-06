# GATE 1 Physical Action Packet

Generated: 2026-08-06T20:16:47Z

## Equipment inventory command

```bash
python -m gate1.orchestrator.cli status --equipment-inventory
```

**Assumption:** Equipment existence is NEVER assumed.

## Inventory (default — does not claim equipment exists)

| Item | Status | Blocker |
|---|---|---|
| representative_boot_hardware | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |
| ring_prototype | MISSING_ASSUMED | REQUIRES_PHYSICAL_PROTOTYPE |
| dock_station | MISSING_ASSUMED | REQUIRES_PHYSICAL_PROTOTYPE |
| on_device_ai_runtime_target | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |
| game_target_device | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |

## Exact steps

### A. Boot (G1-C1)
1. Run equipment inventory; confirm representative hardware is PRESENT (do not assume).
2. Image/boot candidate per `gunnchos-device-os` boot_readiness docs.
3. Capture device identity, boot duration, service health, storage, display/input, network.
4. Write physical evidence JSON (`evidence_class=physical`, `claim_level=PHYSICAL_BOOT`).
5. `python -m gate1.orchestrator.cli ingest-evidence <path>` then operator-move to `accepted/`.

### B. Ring authenticated input (G1-C2)
1. Inventory ring prototype; if MISSING, stop — do not fabricate.
2. Pair ring using documented auth path (hardware-industrial-design / edge-io / device-os).
3. Capture authenticated frame with anti-replay nonce and payload digest.
4. Ingest physical evidence (`claim_level=PHYSICAL_RING`).

### C. Dock continuity (G1-C3)
1. Inventory dock station; if MISSING, stop.
2. Dock device; record power negotiation, display handoff, session continuity.
3. Ingest physical evidence (`claim_level=PHYSICAL_DOCK`).

### D. Local AI runtime (G1-C4)
1. Inventory on-device AI target; if MISSING, stop.
2. Start gunnchAI3k local-only mode; verify network egress denied.
3. Capture runtime health + version; ingest (`claim_level=PHYSICAL_AI_DEVICE`).

### E. Game core loops (G1-C5)
For each game — beatlink-party, archive-of-life-artifact-world, pedestrian-pursuit, anime-aggressors:
1. Confirm target device PRESENT via inventory.
2. Launch software harness/runtime available in that repo.
3. Complete one core loop; record steps_completed.
4. Ingest physical evidence (`claim_level=PHYSICAL_GAME_DEVICE`, workstream=games).

## Acceptance
- Only files under `gate1/evidence/accepted/` with `evidence_class=physical` upgrade physical claims.
- Simulated/software evidence must remain classified as such.
