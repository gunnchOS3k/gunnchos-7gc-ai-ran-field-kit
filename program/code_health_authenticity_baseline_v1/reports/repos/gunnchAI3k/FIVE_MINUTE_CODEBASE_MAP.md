# Five-minute codebase map — `gunnchAI3k`

Accepted main: `4b4f411710e8`

## What this repo is
- Classified files: **658** (code=375, production≈262, proof≈74)
- Entrypoints: package.json, Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `FAIL_COUPLED`
- Runtime authenticity: `NEEDS_WORK`
- Theater: S0=276 S1=68 total=344
- Hotspots: 2; wave-dup paths: 35; orphans≈0

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
- `mutation_resistance`: **NOT_APPLICABLE**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S0` `assert_true_literal` at `tests/reactivation.test.ts:74`
- Hottest function: `scripts/prove_phase_xiv_ai.py::main` complexity=23
