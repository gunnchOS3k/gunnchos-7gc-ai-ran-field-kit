# Gate 1 evidence store

Directories:

- `pending/` — machine-written JSON from `python -m gate1.orchestrator.cli run` and `ingest-evidence`
- `accepted/` — human/operator-accepted evidence only (required for physical claim upgrades)
- `rejected/` — failed validation or tamper/hash mismatches

Rules:

1. Separate `simulated`, `software`, and `physical` evidence classes.
2. Never promote a physical claim from simulated/software evidence.
3. `GATE_1_AUTOMATED_PASS` is allowed when software slices pass and physical is pending.
4. `GATE_1_PASS` requires accepted physical evidence for boot, ring-auth, dock, ai-runtime, and all four games.
