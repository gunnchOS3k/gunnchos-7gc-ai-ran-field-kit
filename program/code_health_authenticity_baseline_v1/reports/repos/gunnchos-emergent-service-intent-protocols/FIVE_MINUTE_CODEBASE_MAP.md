# Five-minute codebase map — `gunnchos-emergent-service-intent-protocols`

Accepted main: `088c5e88e155`

## What this repo is
- Classified files: **536** (code=75, production≈42, proof≈22)
- Entrypoints: Makefile, pyproject.toml

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=0 S1=5 total=5
- Hotspots: 31; wave-dup paths: 0; orphans≈31

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **NEEDS_WORK**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **ADEQUATE**
- `complexity_hotspots`: **NEEDS_WORK**
- `orphan_dead_code`: **NEEDS_WORK**
- `fixture_honesty`: **STRONG**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **CRITICAL**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S1` `assert_equals_self` at `tests/unit/test_interpretability_metrics.py:40`
- Hottest function: `src/emergent_intent/comm/channel.py::exchange` complexity=38
