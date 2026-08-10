# WP-008 — EVT0 NFR Target Freeze

Implementer artifacts for Operating Cycle 2 WP-008.

## Exit artifacts

| File | Role |
|---|---|
| `EVT0_NFR_TARGET_REGISTRY.json` | Canonical frozen targets |
| `EVT0_NFR_SOURCE_LEDGER.md` | Sources / dates / confidence |
| `EVT0_COMPETITOR_TARGET_MATRIX.json` | Strategy → NFR map (`competitor_score` null) |
| `EVT0_TARGET_MEASUREMENT_MAP.json` | Metric → method/instrument map |
| `EVT0_TBD_RESIDUALS.json` | Honest residual TBDs |
| `validate_evt0_nfr_freeze.py` | Integrity check (not VP-008) |

## Token prepared for verifier

`NFR_TARGETS_FROZEN_FOR_EVT0` (implementer-prepared; independent VP-008 decides PASS).

## Non-claims

- No `VP-008-RESULT.json`
- No fabricated competitor scores
- No frontier parity
- WP-010 instruments marked `TBD_WP010` until that packet lands
