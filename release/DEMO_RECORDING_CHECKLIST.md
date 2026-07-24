# Demo Recording Checklist

## Before recording

- [ ] Confirm branch/commit hash on screen
- [ ] Confirm pilot status **0/54** stated verbally
- [ ] Confirm **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** stated for any results slide
- [ ] No synthetic CSVs presented as field measurements
- [ ] No invented DOI, submission ID, or outcome numbers

## Environment

- [ ] Python env matches `ENVIRONMENT.md`
- [ ] `make test` passes
- [ ] Sibling repos available if integrated demo uses `REPOS_ROOT`

## On-screen artifacts

- [ ] `GATE1_LOCKED_RESEARCH_THESIS.md`
- [ ] `contracts/` + valid/invalid fixture example
- [ ] `pilot/54_CELL_ASSIGNMENT_MATRIX.csv`
- [ ] `evaluation/PRIMARY_OUTCOME_LOCK.json`
- [ ] `paper/main.tex` or `paper/README.md`
- [ ] `release/CLAIM_BOUNDARIES.md`

## Audio / accessibility

- [ ] Read claim boundaries table aloud
- [ ] Spell acronyms once (AI-RAN, NTN, O-RAN)
- [ ] Caption file planned if publishing video

## After recording

- [ ] Attach commit hash and manifest checksum file to video description
- [ ] Do not upload raw-private data
- [ ] File recording path in human action queue if public release planned
