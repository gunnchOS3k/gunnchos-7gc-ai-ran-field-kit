# Five-minute codebase map — `edge-io-measurement-node`

Accepted main: `af57fbdac857`

## What this repo is
- Classified files: **6024** (code=2068, production≈1982, proof≈38)
- Entrypoints: Makefile

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `FAIL_COUPLED`
- Runtime authenticity: `NEEDS_WORK`
- Theater: S0=0 S1=196 total=196
- Hotspots: 1393; wave-dup paths: 0; orphans≈40

## Dimension ratings
- `production_proof_separation`: **CRITICAL**
- `anti_test_theater`: **NEEDS_WORK**
- `dependency_boundaries`: **NEEDS_WORK**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **NEEDS_WORK**
- `complexity_hotspots`: **CRITICAL**
- `orphan_dead_code`: **NEEDS_WORK**
- `fixture_honesty`: **ADEQUATE**
- `documentation_readability`: **ADEQUATE**
- `mutation_resistance`: **ADEQUATE**

## First files to read
1. README.md (if present)
2. Entrypoint from list above
3. One production module and one test that claims to exercise it
4. Any `artifacts/**/ACCEPTANCE.json` or RESULT json — treat as proof, not product

## Maintainability risks (this scan)
- Top theater hit: `S1` `todo_pass` at `.venv-zephyr/bin/hexmerge.py:178`
- Hottest function: `.venv-zephyr/lib/python3.11/site-packages/setuptools/config/_validate_pyproject/fastjsonschema_validations.py::validate_https___setuptools_pypa_io_en_latest_references_keywords_html` complexity=351
