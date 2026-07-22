# POST_MERGE_GATE3_TEST_REPORT

Generated: 2026-07-22T17:10:05.764565+00:00

## Promotion merge tests (on each repo after merge)

| Repo | Command | Result |
|---|---|---|
| edge-io-measurement-node | `PYTHONPATH=src pytest -q tests` | 18 passed |
| 7gc-digital-twin | `PYTHONPATH=src pytest -q tests` | 50 passed |
| spectrumx-ai-ran-gary | `PYTHONPATH=src pytest -q tests/gate2` | 4 passed (unrelated tqdm failures in digital_twin_contract) |
| ntn-resilience-sim | `PYTHONPATH=src pytest -q tests` | 22 passed |
| field-kit | `pytest -q tests` | 29+ passed; later 37+ with Gate 4 |
| field-kit | `run_gate3_evidence_pipeline.py --android-builds` | GATE3_COLLECTION_READY initially |

## Post-calibration

| Command | Result |
|---|---|
| gate3 pipeline with sanitized calibration | **GATE3_PARTIAL_EVIDENCE** |
| make gate4-evaluation-ready | **GATE4_EVALUATION_READY** |
