# Five-minute codebase map — `anime-aggressors`

Accepted main: `0afe3079db47`

## What this repo is
- Classified files: **1312** (code=769, production≈449, proof≈215)
- Entrypoints: package.json

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=0 S1=0 total=17
- Hotspots: 3; wave-dup paths: 0; orphans≈0

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **ADEQUATE**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **ADEQUATE**
- `complexity_hotspots`: **ADEQUATE**
- `orphan_dead_code`: **ADEQUATE**
- `fixture_honesty`: **STRONG**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **NOT_APPLICABLE**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S2` `hardcoded_pass_json` at `game-godot/scripts/cross_device/CrossDeviceContractProvider.gd:171`
- Hottest function: `tools/validate_game_rc_contracts.py::main` complexity=28
