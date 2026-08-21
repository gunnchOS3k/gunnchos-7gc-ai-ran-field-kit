# Five-minute codebase map — `archive-of-life-artifact-world`

Accepted main: `069243c36555`

## What this repo is
- Classified files: **574** (code=262, production≈159, proof≈11)
- Entrypoints: package.json, Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `FAIL_COUPLED`
- Runtime authenticity: `NEEDS_WORK`
- Theater: S0=162 S1=50 total=212
- Hotspots: 5; wave-dup paths: 41; orphans≈8

## Dimension ratings
- `production_proof_separation`: **CRITICAL**
- `anti_test_theater`: **CRITICAL**
- `dependency_boundaries`: **NEEDS_WORK**
- `canonical_vs_wave_dup`: **NEEDS_WORK**
- `runtime_authenticity`: **NEEDS_WORK**
- `complexity_hotspots`: **ADEQUATE**
- `orphan_dead_code`: **ADEQUATE**
- `fixture_honesty`: **ADEQUATE**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **NEEDS_WORK**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S0` `assert_true_literal` at `artifacts/game_rc_002/independent_verifier_playthrough.test.ts:172`
- Hottest function: `scripts/validate_game_rc_contracts.py::main` complexity=39
