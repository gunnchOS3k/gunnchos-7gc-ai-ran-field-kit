# Claim Boundaries

Authoritative thesis boundaries: [`GATE1_LOCKED_RESEARCH_THESIS.md`](../GATE1_LOCKED_RESEARCH_THESIS.md)

## Evidence tiers

| Tier | Meaning | Example |
|------|---------|---------|
| Smoke | CI executes | `make test` |
| Synthetic reproducible | Deterministic scripts/fixtures | integrated pipeline on fixtures |
| Controlled device | Authentic pilot sessions | Gate 3 PILOT mode, matrix cell complete |
| Release/archive | Immutable public bundle + reproduction | Gate 5/6 |

## Allowed claims today

- Gate 1 thesis, hypothesis, and RQ1–RQ3 are locked and validated.
- Gate 2 schemas, invalid-fixture rejection, and integrated pipeline pass on fixtures.
- Gate 4 evaluation **infrastructure** is ready; synthetic runs are labeled synthetic.
- Methods manuscript and pilot protocol are documented.
- Pilot matrix status **0/54** is an honest count.

## Forbidden or pending claims

| Claim | Status |
|-------|--------|
| Primary outcome superiority | **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** |
| Pilot completion | **0/54** — pending human collection |
| Calibration as pilot evidence | Forbidden |
| Carrier-grade AI-RAN | **not claimed** |
| Deployable 6G | **not claimed** |
| Citywide / Gary generalization | **not claimed** |
| Unauthorized RF transmission | **not claimed** |
| Zenodo DOI | **DOI_PENDING** |
| Non-author reproduction | **PENDING** |

## Wording guide

Use: **6G-aligned**, **IMT-2030-aligned**, **AI-assisted O-RAN-style**, **phone-first field console**, **exploratory field measurements**, **receive-only SDR observation**.

Avoid: deployed 6G, commercial NTN control, operational near-RT RIC, regulatory certification.

## Results rule

Any public results section must either:

1. State **RESULTS_PENDING_AUTHENTIC_GATE3_DATA**, or
2. Cite authentic Gate 3 artifacts with checksums and consent approval.

Never import Gate 4 synthetic numeric tables as field results.
