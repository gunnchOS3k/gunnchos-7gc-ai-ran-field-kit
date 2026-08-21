# Five-minute codebase map — `spectrumx-ai-ran-gary`

Accepted main: `cef3900af100`

## What this repo is
- Classified files: **474** (code=144, production≈71, proof≈7)
- Entrypoints: Makefile, pyproject.toml

## Where production lives
- Prefer `src/`, `lib/`, `app/`, `game-godot/`, `cmd/`, `pkg/`, runtime `scripts/` (non-test).
- Proof/evidence trees are not product runtime.

## Where proof lives
- `tests/`, `evals/`, `evidence/`, `artifacts/`, fixtures, wave harnesses.

## Authenticity snapshot
- Proof independence: `PASS_INDEPENDENT`
- Runtime authenticity: `ADEQUATE`
- Theater: S0=0 S1=26 total=34
- Hotspots: 51; wave-dup paths: 0; orphans≈40

## Dimension ratings
- `production_proof_separation`: **STRONG**
- `anti_test_theater`: **NEEDS_WORK**
- `dependency_boundaries`: **ADEQUATE**
- `canonical_vs_wave_dup`: **STRONG**
- `runtime_authenticity`: **ADEQUATE**
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
- Top theater hit: `S1` `todo_pass` at `paper/scripts/generate_tables.py:274`
- Hottest function: `apps/streamlit_app.py::_render_judge_gary_micro_twin_3d` complexity=395
