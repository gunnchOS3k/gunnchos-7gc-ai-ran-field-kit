# Five-minute codebase map — `gunnchos-research-portal`

Accepted main: `afb2bab2b415`

## What this repo is
- Classified files: **114** (code=8, production≈0, proof≈0)
- Entrypoints: Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `NOT_APPLICABLE_NO_PRODUCTION_CODE`
- Runtime authenticity: `NOT_APPLICABLE`
- Theater: S0=0 S1=5 total=8
- Hotspots: 11; wave-dup paths: 0; orphans≈0

## Dimension ratings
- `production_proof_separation`: **NEEDS_WORK**
- `anti_test_theater`: **NEEDS_WORK**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **NOT_APPLICABLE**
- `complexity_hotspots`: **CRITICAL**
- `orphan_dead_code`: **ADEQUATE**
- `fixture_honesty`: **STRONG**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **CRITICAL**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S1` `todo_pass` at `scripts/validate_supervisor_ready.py:160`
- Hottest function: `scripts/run_vp012_portal_first.py::main` complexity=46
