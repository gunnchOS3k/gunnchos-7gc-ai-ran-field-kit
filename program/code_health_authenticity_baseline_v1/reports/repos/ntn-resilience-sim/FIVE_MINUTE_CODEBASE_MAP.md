# Five-minute codebase map — `ntn-resilience-sim`

Accepted main: `916520919bea`

## What this repo is
- Classified files: **390** (code=50, production≈30, proof≈13)
- Entrypoints: Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=0 S1=7 total=7
- Hotspots: 6; wave-dup paths: 0; orphans≈15

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **NEEDS_WORK**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **ADEQUATE**
- `complexity_hotspots`: **CRITICAL**
- `orphan_dead_code`: **NEEDS_WORK**
- `fixture_honesty`: **STRONG**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **NOT_APPLICABLE**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S1` `todo_pass` at `paper/scripts/generate_tables.py:368`
- Hottest function: `paper/scripts/generate_tables.py::main` complexity=71
