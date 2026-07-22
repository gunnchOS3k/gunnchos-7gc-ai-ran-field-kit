# Gate 3 — Gate 2 Baseline Verification

Verification time (UTC): 2026-07-22T15:55:11.938752+00:00

All expected Gate 2 commits matched. Field-kit had a transient uncommitted `.gitignore` edit that was restored before branching.

## Repository verification

| Repository | Parent branch | Expected commit | Actual commit | Dirty | Match |
|---|---|---|---|---|---|
| gunnchos-7gc-ai-ran-field-kit | cursor/gate2-integrated-system-3ec5 | 82099df12323c9b689e55f8a1169781416e406b5 | 82099df12323c9b689e55f8a1169781416e406b5 | clean after restore | MATCH |
| edge-io-measurement-node | cursor/gate2-integrated-system-3ec5 | 9d04dd5bf3b726b21b76718ee80c7c2f5c6c18f7 | 9d04dd5bf3b726b21b76718ee80c7c2f5c6c18f7 | clean | MATCH |
| 7gc-digital-twin | cursor/gate2-integrated-system-3ec5 | 323a88ca21b7ff7bee2a8549cddb09da96b0ed1b | 323a88ca21b7ff7bee2a8549cddb09da96b0ed1b | clean | MATCH |
| spectrumx-ai-ran-gary | cursor/gate2-integrated-system-3ec5 | 0686d47d77cbc9fb9cbce262cdae732996f106b5 | 0686d47d77cbc9fb9cbce262cdae732996f106b5 | clean | MATCH |
| ntn-resilience-sim | cursor/gate2-integrated-system-3ec5 | ea7800e22409f2d7b6a41e22560f81d59043475e | ea7800e22409f2d7b6a41e22560f81d59043475e | clean | MATCH |
| readygary-6g-beam-selection | cursor/gate2-integrated-system-3ec5 | a4b75f719fcc94170968af9791ce9f621cf4bd85 | a4b75f719fcc94170968af9791ce9f621cf4bd85 | clean | MATCH |

## Commands executed

| Repository | Command | Result | Notes |
|---|---|---|---|
| field-kit | `python3 -m pytest -q tests` | 19 passed | contract + failure + provenance |
| edge-io | `pytest -q tests/contracts` | 11 passed | |
| 7gc | `pytest -q tests/gate2` | 6 passed | |
| spectrumx | `pytest -q tests/gate2` | 4 passed | |
| ntn | `pytest -q tests/gate2` | 5 passed | |
| field-kit | `python3 scripts/run_integrated_pipeline.py ... --strict` | ok | AUTOMATED_PIPELINE_PASS |

## Integrated run

- run_id: `2026-07-22-synthetic-gary-learn-001`
- evidence_level: synthetic
- gate2_status: AUTOMATED_PIPELINE_PASS
- output: `results/integrated/2026-07-22-synthetic-gary-learn-001/`
- selected AI-RAN policy: twin_informed
- selected resilience mode: terrestrial

## Differences from prior Cursor report

None for commits. Gate 2 base is intact. Gate 3 work proceeds on stacked branch `cursor/gate3-genuine-evidence`.
