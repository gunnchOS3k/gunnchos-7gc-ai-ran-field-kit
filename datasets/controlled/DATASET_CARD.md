# Controlled Dataset Card

**Gate 3 status:** **HUMAN_ACTION_REQUIRED** — **0/54** eligible pilot cells  
**Results:** **RESULTS_PENDING_AUTHENTIC_GATE3_DATA**

## Dataset types

| Path | Visibility | Description |
|------|------------|-------------|
| `raw-private/` | gitignored local | Raw device exports |
| `session-manifests/` | public scaffolding | Session manifest placeholders |
| `sanitized/` | gitignored until approved | Privacy-reviewed derivatives |
| `published/` | public when approved | Publication-ready sanitized bundles |
| `coverage/` | public | 54-cell coverage matrix (counts only) |

## Pilot design

- Matrix: 3 zones × 2 network conditions × 3 days × 3 workloads = **54** cells
- Authoritative design: `pilot/54_CELL_ASSIGNMENT_MATRIX.csv`
- Coverage tracker: `coverage/PILOT_COVERAGE_MATRIX.csv` (**0/54** complete)

## Labels

- `synthetic` — fixtures/simulation only
- `controlled_device_measurement` — authentic device session
- `calibration_only` — infrastructure validation, excluded from pilot counts
- `rehearsal` — excluded from pilot counts

## Privacy

See `privacy-summary/README.md` and root `docs/PRIVACY_AND_ETHICS.md`.
Raw exports never committed.

## Provenance

Empty structure until sanitization: `RAW_TO_SANITIZED_PROVENANCE.json`

## Release cross-link

Release bundle summary: [`release/DATASET_CARD.md`](../../release/DATASET_CARD.md)

## Missing data

See `MISSING_DATA_REPORT.md` — all 54 cells pending at freeze.
