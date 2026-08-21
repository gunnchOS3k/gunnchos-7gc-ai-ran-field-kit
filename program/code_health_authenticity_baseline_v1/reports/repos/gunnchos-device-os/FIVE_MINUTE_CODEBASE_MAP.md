# Five-minute codebase map — `gunnchos-device-os`

Accepted main: `28562a845620`

## What this repo is
- Classified files: **2771** (code=1089, production≈180, proof≈207)
- Entrypoints: Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `FAIL_COUPLED`
- Runtime authenticity: `NEEDS_WORK`
- Theater: S0=0 S1=0 total=80
- Hotspots: 338; wave-dup paths: 101; orphans≈40

## Dimension ratings
- `production_proof_separation`: **CRITICAL**
- `anti_test_theater`: **ADEQUATE**
- `dependency_boundaries`: **NEEDS_WORK**
- `canonical_vs_wave_dup`: **ADEQUATE**
- `runtime_authenticity`: **NEEDS_WORK**
- `complexity_hotspots`: **CRITICAL**
- `orphan_dead_code`: **NEEDS_WORK**
- `fixture_honesty`: **ADEQUATE**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **NEEDS_WORK**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S2` `broad_except_pass` at `artifacts/wp007/independent_verifier/run_independent_attacks.py:1124`
- Hottest function: `gunnchos_device_os/device_lab/interactive_guest_proofs.py::attempt_ring_app_mutation_pass` complexity=204
