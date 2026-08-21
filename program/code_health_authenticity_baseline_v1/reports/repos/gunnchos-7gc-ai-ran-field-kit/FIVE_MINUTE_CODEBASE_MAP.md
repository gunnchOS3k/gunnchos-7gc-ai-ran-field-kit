# Five-minute codebase map — `gunnchos-7gc-ai-ran-field-kit`

Accepted main: `556f2815a0b3`

## What this repo is
- Classified files: **2586** (code=379, production≈2, proof≈89)
- Entrypoints: Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=2 S1=252 total=263
- Hotspots: 187; wave-dup paths: 310; orphans≈1

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **CRITICAL**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **NEEDS_WORK**
- `runtime_authenticity`: **ADEQUATE**
- `complexity_hotspots`: **CRITICAL**
- `orphan_dead_code`: **ADEQUATE**
- `fixture_honesty`: **ADEQUATE**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **ADEQUATE**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S0` `always_pass_gate` at `research/external_reproduction/oulu001_fr3_mmwave.py:161`
- Hottest function: `scripts/validate_digital_ecosystem_baseline_v2.py::main` complexity=114
