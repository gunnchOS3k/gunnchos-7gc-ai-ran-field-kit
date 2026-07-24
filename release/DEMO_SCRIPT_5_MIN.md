# 5-Minute Demo Script

**Audience:** reviewers, collaborators  
**Evidence shown:** synthetic/fixture pipeline only — **not field pilot results**

## 0:00 — Title and boundaries (30 s)

- Title: Resilience-Aware, Human-Centric AI-RAN Orchestration…
- State: research prototype; **0/54 pilot cells**; results **RESULTS_PENDING_AUTHENTIC_GATE3_DATA**
- Show `release/CLAIM_BOUNDARIES.md` headline table

## 0:30 — Gate 1 thesis (45 s)

- Open `GATE1_LOCKED_RESEARCH_THESIS.md`
- Point to hypothesis and RQ1–RQ3
- Emphasize non-goals (no deployable 6G)

## 1:15 — Contracts (60 s)

- List `contracts/` schemas
- Show one valid fixture vs one invalid fixture rejection reason

## 2:15 — Integrated pipeline (90 s)

```bash
pip install -r requirements.txt
make test
make integrated-pipeline EDGE_INPUT=fixtures/valid/edge_measurement_batch.valid.json
```

- Show latest `results/integrated/*/validation_report.json`
- Label output **synthetic / fixture-backed**

## 3:45 — Pilot protocol (45 s)

- Open `pilot/54_CELL_ASSIGNMENT_MATRIX.csv` — all `pending_design_approval`
- Mention consent, privacy scan, PILOT-only counting
- Raw data stays in gitignored `datasets/controlled/raw-private/`

## 4:30 — Evaluation preregistration (30 s)

- Open `evaluation/PRIMARY_OUTCOME_LOCK.json` — outcome `recovery_time_s`
- State analysis runs only after authentic Gate 3 data

## 4:50 — Close (10 s)

- Methods manuscript: `paper/main.tex`
- Release checklist: `release/RELEASE_CHECKLIST.md`
- DOI: **DOI_PENDING**
