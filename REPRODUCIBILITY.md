# Reproducibility

**Results status:** **RESULTS_PENDING_AUTHENTIC_GATE3_DATA**  
**Pilot matrix:** **0/54** eligible cells

## What is reproducible today

| Target | Command | Evidence label |
|--------|---------|----------------|
| Contract tests | `make contract-test` | smoke + schema |
| Unit tests | `make test` | smoke |
| Gate 1 thesis lock | `make gate1-validate` | proven |
| Integrated pipeline | `make integrated-pipeline EDGE_INPUT=fixtures/valid/edge_measurement_batch.valid.json` | synthetic/fixture |
| Provenance verify | `make reproduce` | synthetic/fixture |

Sibling repositories under `REPOS_ROOT` (default parent directory) are required for full integrated runs — see [`ENVIRONMENT.md`](ENVIRONMENT.md).

## What is not reproducible without human action

- Authentic Gate 3 pilot sessions (raw-private, gitignored)
- Sanitized publication derivatives pending approval
- Primary-outcome statistical inference on field data
- Immutable release tarball + DOI (**DOI_PENDING**)
- Non-author independent reproduction (**PENDING**)

## Reproduction reports

| Report | Purpose | Status |
|--------|---------|--------|
| [`AUTHOR_REPRODUCTION_REPORT.md`](AUTHOR_REPRODUCTION_REPORT.md) | Author clean-checkout | **PENDING** |
| [`NON_AUTHOR_REPRODUCTION_TEMPLATE.md`](NON_AUTHOR_REPRODUCTION_TEMPLATE.md) | Independent replicator form | template |
| [`NON_AUTHOR_REPRODUCTION_REPORT.md`](NON_AUTHOR_REPRODUCTION_REPORT.md) | Filed independent results | **PENDING** (empty) |

## Claim boundaries

Engineering pass (Gate 2) does not imply field evidence (Gate 3) or release completion (Gate 5/6).
See [`release/CLAIM_BOUNDARIES.md`](release/CLAIM_BOUNDARIES.md).

## Manuscript

Methods sources: [`paper/main.tex`](paper/main.tex) — results section states **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** only.

## Checksums

Public artifact hashes: [`release/CHECKSUMS.sha256`](release/CHECKSUMS.sha256) aligned with [`release/ARTIFACT_MANIFEST.json`](release/ARTIFACT_MANIFEST.json).
