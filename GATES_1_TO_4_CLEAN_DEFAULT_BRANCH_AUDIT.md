# GATES_1_TO_4_CLEAN_DEFAULT_BRANCH_AUDIT

Generated: 2026-07-23T00:34:20.502262+00:00

## Summary

Clean default-branch checkouts audited. Featured repositories are on current remote tips with clean working trees.

| Repository | Default | SHA | Latest merged PR | Tests | Status-doc accuracy | Required correction |
|---|---|---|---|---|---|---|
| gunnchos-7gc-ai-ran-field-kit | `master` | `802d8b4aa900d4c9faa07b785cac44253b7c0eb7` | #5 Gate 3/4 continuation: calibration, pilotctl, Gate 4 evaluation readiness | `python3 -m pytest -q tests` → 48+ passed on branch; full suite after changes | see below | Lock Gate1; normalize Gate2 taxonomy; update repo-lock; regenerate clean proof; correct README status table. |
| edge-io-measurement-node | `main` | `764192fd889bd42246096402d3ea573d85b1f923` | #22 Gate 3 continuation: Android build report and device preflight | `PYTHONPATH=src pytest -q tests` → 18 passed | see below | No required code change in this cloud closure (field-kit authority sufficient). |
| 7gc-digital-twin | `main` | `fcc9b11df3be2205efc501e724745b6947563be7` | #27 fix(gate2): tolerate null unavailable physical metrics | `PYTHONPATH=src pytest -q tests` → 50 passed | see below | No required code change. |
| spectrumx-ai-ran-gary | `main` | `f7af6c7f7541360e07402f6927794116a1684d32` | #96 Gate 3 promotion: synthetic evidence safeguards | `PYTHONPATH=src pytest -q tests/gate2` → 4 passed | see below | No required code change. |
| ntn-resilience-sim | `main` | `2403456d03d5eba6e4f56c0fd9e18e141ed2761a` | #24 Gate 3 continuation: TR 38.821 section pointers for NTN assumptions | `PYTHONPATH=src pytest -q tests` → 22 passed | see below | No required code change. |
| readygary-6g-beam-selection | `main` | `525405cb19d7987ad218272f5897d4917c10dd75` | #23 Gate 2: document optional beam provider role | `optional` → not required for Gates 1–4 | see below | Remain optional. |

## Per-repository notes

### gunnchos-7gc-ai-ran-field-kit

- Default branch: `master`
- Exact SHA: `802d8b4aa900d4c9faa07b785cac44253b7c0eb7`
- Clean working tree: True
- Stale information: README still described AUTOMATED_PIPELINE_PASS as Gate2 end-state; NO_DEVICE notes in older PR bodies are historical cloud checkpoints superseded by local Pixel calibration reports.
- Required correction: Lock Gate1; normalize Gate2 taxonomy; update repo-lock; regenerate clean proof; correct README status table.

### edge-io-measurement-node

- Default branch: `main`
- Exact SHA: `764192fd889bd42246096402d3ea573d85b1f923`
- Clean working tree: True
- Stale information: Earlier PR #22 text mentioned NO_DEVICE; superseded by merged Pixel calibration evidence in field-kit reports.
- Required correction: No required code change in this cloud closure (field-kit authority sufficient).

### 7gc-digital-twin

- Default branch: `main`
- Exact SHA: `fcc9b11df3be2205efc501e724745b6947563be7`
- Clean working tree: True
- Stale information: No major stale Gate status table; null-metric PR merged.
- Required correction: No required code change.

### spectrumx-ai-ran-gary

- Default branch: `main`
- Exact SHA: `f7af6c7f7541360e07402f6927794116a1684d32`
- Clean working tree: True
- Stale information: Gate3 note present; no Gate1 lock authority (correct — field-kit owns it).
- Required correction: No required code change.

### ntn-resilience-sim

- Default branch: `main`
- Exact SHA: `2403456d03d5eba6e4f56c0fd9e18e141ed2761a`
- Clean working tree: True
- Stale information: Assumption registry on main with TR 38.821 pointers.
- Required correction: No required code change.

### readygary-6g-beam-selection

- Default branch: `main`
- Exact SHA: `525405cb19d7987ad218272f5897d4917c10dd75`
- Clean working tree: True
- Stale information: Optional role documented; must remain non-blocking.
- Required correction: Remain optional.
