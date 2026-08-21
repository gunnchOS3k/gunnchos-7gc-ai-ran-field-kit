# Five-minute codebase map — `waike-research-ops`

Accepted main: `5d416c09164c`

## What this repo is
- Classified files: **7145** (code=151, production≈72, proof≈18)
- Entrypoints: Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=0 S1=0 total=1
- Hotspots: 25; wave-dup paths: 0; orphans≈0

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **ADEQUATE**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **ADEQUATE**
- `complexity_hotspots`: **CRITICAL**
- `orphan_dead_code`: **ADEQUATE**
- `fixture_honesty`: **ADEQUATE**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **CRITICAL**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S2` `hardcoded_pass_json` at `scripts/detect_templated_courses.py:24`
- Hottest function: `src/waike_course_ready/provenance.py::audit` complexity=60
