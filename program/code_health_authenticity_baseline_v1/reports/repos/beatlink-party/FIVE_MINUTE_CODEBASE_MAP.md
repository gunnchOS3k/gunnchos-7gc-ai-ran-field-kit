# Five-minute codebase map — `beatlink-party`

Accepted main: `23a95d152c2d`

## What this repo is
- Classified files: **318** (code=134, production≈90, proof≈34)
- Entrypoints: package.json, Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=0 S1=0 total=93
- Hotspots: 1; wave-dup paths: 43; orphans≈0

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **ADEQUATE**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **ADEQUATE**
- `runtime_authenticity`: **ADEQUATE**
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
- No static theater hits in scanned sample.
- Hottest function: `scripts/validate_game_rc_contracts.py::main` complexity=35
