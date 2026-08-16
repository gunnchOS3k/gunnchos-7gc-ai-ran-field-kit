# C-PKT-002 Owner Merge Packet (DRAFT — Cursor never merges)

## What landed
- `research/external_reproduction/` NVIDIA×Oulu registry, fail-closed adapters, bridge, researcher CLI
- OULU-001 / OULU-002 full artifact packs (CPU analytical)
- OULU-003/004 + NVIDIA-001/002 preparation specs only
- Claim firewall: SoA/PHYSICAL/OTA/CERTIFIED/CARRIER forced false

## Classifications
| Target | Token |
|--------|--------|
| OULU-001 → R6G-003 | `REFERENCE_SPEC_INCOMPLETE` |
| OULU-002 → R6G-004/006 | `BASELINE_MATCH_PENDING` |
| Targets 3–6 | `PREPARATION_ONLY` |

## Env
Host: Apple M2, no CUDA/Sionna/AODT/pyAerial/Aerial — all GPU backends `UNAVAILABLE_FAIL_CLOSED`.

## Merge readiness
**YES** for digital honesty + scaffolding (Edmund). Not a SoA or Aerial PASS.

## Do not
- Merge via Cursor
- Edit WAIKE (no DIGITAL_REPRODUCTION_PASS)
- Claim PHYSICAL / OTA / CERTIFIED / CARRIER
