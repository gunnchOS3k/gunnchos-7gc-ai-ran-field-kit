# Local Release Candidate Audit

**Generated:** 2026-07-24T15:05:00Z  
**Command:** `make release-candidate`  
**Archive:** `release/dist/gunnchos-7gc-ai-ran-field-kit-public-20260724T150454Z.tar.gz`  
**Checksum:** `release/dist/gunnchos-7gc-ai-ran-field-kit-public-20260724T150454Z.sha256`  
**DOI:** **DOI_PENDING** — not deposited

---

## Executive summary

Release candidate tooling builds a **public** tarball from `release/ARTIFACT_MANIFEST.json`. The archive contains 36 files (methods, contracts, fixtures, preregistration, pilot design docs). **No raw-private paths** are included. Scientific results are not claimed (`RESULTS_PENDING_AUTHENTIC_GATE3_DATA`; Gate 3 **0/54**).

PR #8 is **merged** into `master` at `5e85190ee17540933af93eda759dd1e809710edf` (2026-07-24T01:56:56Z).

---

## Build verification

| Check | Result |
|-------|--------|
| `make release-candidate` exit 0 | PASS |
| Manifest present | `release/ARTIFACT_MANIFEST.json` |
| SHA256 sidecar written | PASS |
| File count | 36 |

---

## Exclusion audit (critical)

Manifest `excluded_private` entries:

- `datasets/controlled/raw-private/**`
- `datasets/controlled/raw/**`
- `results/calibration/**/sanitized_*.json`

**Tarball scan:** no paths matching `raw-private` or `datasets/controlled/raw/` present.

Included controlled data artifact: `datasets/controlled/DATASET_CARD.md` only (metadata card, no raw captures).

---

## Claim boundaries

| Claim | Allowed |
|-------|---------|
| Gate 2 integrated system reproducibility | YES (fixture-backed) |
| Methods-ready paper sources in repo | YES (`paper/main.tex`; PDF built locally at `paper/main.pdf` — not in manifest tarball) |
| Scientific pilot results | NO |
| DOI issued | NO — DOI_PENDING |
| Gate 4 PASS | NO — BLOCKED |

---

## Gaps before Zenodo deposit

1. Authentic Gate 3–4 results (when available)
2. Assign DOI via Zenodo using `release/ZENODO_METADATA.json`
3. Tag release on GitHub after deposit
4. Optional: add `paper/main.pdf` to manifest if public PDF release intended

---

## Verdict

**Local release candidate build:** PASS (tooling + exclusions)  
**Public scientific release / DOI:** EXTERNAL_DEPENDENCY — DOI_PENDING
