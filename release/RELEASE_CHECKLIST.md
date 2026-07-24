# Release Checklist

Gate 5/6 release evidence remains **RELEASE_EVIDENCE_PENDING** at checklist freeze.

## Pre-release (engineering)

- [x] Gate 1 locked thesis validated (`make gate1-validate`)
- [x] Gate 2 contracts and integrated pipeline executable (`make test`, `make integrated-pipeline`)
- [x] Methods manuscript sources present (`paper/main.tex`)
- [x] Preregistration and primary outcome lock present (`evaluation/`)
- [ ] Author clean-checkout reproduction filed (`AUTHOR_REPRODUCTION_REPORT.md` — **PENDING**)
- [ ] Non-author reproduction filed (`NON_AUTHOR_REPRODUCTION_REPORT.md` — **PENDING**)

## Pilot evidence (Gate 3)

- [ ] **0/54** → target 54/54 eligible pilot cells (`pilot/54_CELL_ASSIGNMENT_MATRIX.csv`)
- [ ] Raw-private storage populated locally (gitignored)
- [ ] Sanitized derivatives approved for publication
- [ ] Consent and privacy summaries approved (`datasets/controlled/consent-summary/`, `privacy-summary/`)
- [ ] Protocol deviation log reviewed
- [ ] `datasets/controlled/GATE3_FINAL_REPORT.md` updated with authentic counts

## Scientific evaluation (Gate 4)

- [x] Evaluation infrastructure ready on synthetic/fixture inputs (`GATE4_EVALUATION_READY`)
- [ ] Primary outcome analysis on **authentic Gate 3 data only**
- [ ] Negative/neutral and failure-boundary reports updated with real numbers

## Release artifact bundle

- [x] `release/ARTIFACT_MANIFEST.json` lists public paths
- [x] `release/CHECKSUMS.sha256` hashes manifest entries
- [x] `release/CLAIM_BOUNDARIES.md`
- [x] `release/CONTRIBUTIONS.md`
- [x] `release/DEMO_SCRIPT_5_MIN.md`
- [x] `release/DEMO_RECORDING_CHECKLIST.md`
- [x] `release/DOI_DEPOSIT_INSTRUCTIONS.md`
- [x] `release/build_release_archive.sh`
- [ ] `release/CITATION.cff` — no DOI until deposit (**DOI_PENDING**)
- [ ] Immutable release tag created by human approver (**not automation**)
- [ ] Zenodo (or equivalent) deposit completed (**DOI_PENDING**)

## Human approval

- [ ] Edmund Gunn Jr. release approval
- [ ] Privacy/consent publication approval for any sanitized dataset

## Explicit non-goals

Do not tag, publish, or assign a DOI from CI automation.
Do not invent checksums, result tables, or bibliography entries.
