# GATE 1 Final Acceptance Matrix

Generated: 2026-08-07T20:48:01Z

| Criterion | Software | Physical | Remote CI | Accepted |
|---|---|---|---|---|
| G1-C1 Boot | automatable | PENDING | PENDING | No |
| G1-C2 Ring auth | automatable | PENDING | PENDING | No |
| G1-C3 Dock | automatable | PENDING | PENDING | No |
| G1-C4 Local AI | automatable | PENDING | PENDING | No |
| G1-C5 Games (×4) | automatable | PENDING | PENDING | No |
| Runtime hygiene | PASS | n/a | PENDING | Yes (local) |
| Post-merge integrity audit | PASS | n/a | PENDING | Yes (local) |

## Tokens
- `GATE_1_LOCAL_AUTOMATION_PASS`
- `GATE_1_REMOTE_CI_PENDING`
- `GATE_1_PHYSICAL_EVIDENCE_PENDING`
- `GATE_1_PASS` — not earned

## Acceptance authority
- Physical bundles require Edmund decision record via `python -m gate1.operator.cli accept-bundle`.
