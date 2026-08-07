# Gate 1 evidence store

Directories:

- `pending/` — machine-written JSON from `python -m gate1.orchestrator.cli run` and `ingest-evidence` (gitignored except `.gitkeep`)
- `runs/` — orchestrator run/status aggregates (gitignored except `.gitkeep`)
- `accepted/` — human/operator-accepted evidence only (required for physical claim upgrades)
- `rejected/` — failed validation or tamper/hash mismatches
- `pending/sessions/` — operator physical evidence sessions (runtime only)

Rules:

1. Separate `simulated`, `software`, and `physical` evidence classes.
2. Never promote a physical claim from simulated/software evidence.
3. Timestamped runtime outputs must not be git-tracked; use fixtures under `gate1/fixtures/` for deterministic samples.
4. `GATE_1_LOCAL_AUTOMATION_PASS` / `GATE_1_AUTOMATED_PASS` are allowed when software slices pass and physical is pending.
5. `GATE_1_PASS` requires accepted physical evidence for boot, ring-auth, dock, ai-runtime, and all four games — via `python -m gate1.operator.cli accept-bundle` with an Edmund decision record (never auto-accept).
6. Dry runs: `python -m gate1.orchestrator.cli run --no-write` or `--output-dir <tmp>`.
