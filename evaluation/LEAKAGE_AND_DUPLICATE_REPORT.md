# Leakage and Duplicate Report

**Generated:** 2026-07-24T15:05:00Z  
**Scope:** Synthetic-fixture dry-runs and current pilot inventory  
**Scientific Gate 4:** **BLOCKED**

---

## Summary

No authentic eligible Gate 3 sessions exist (**0/54**), so train/holdout leakage across physical pilot assignments cannot yet occur. Dry-run evaluation uses isolated synthetic fixtures with explicit non-eligibility labels. Duplicate assignment-hash checks are structurally implemented but not exercised on a 54-session corpus.

---

## Data classes in repository

| Class | Location | Eligible for Gate 3/4 science |
|-------|----------|--------------------------------|
| Valid JSON fixtures | `fixtures/valid/` | NO |
| Calibration (local) | `results/calibration/**` | NO — non-counting |
| Rehearsal | `pilot/` rehearsal paths | NO — excluded by protocol |
| Sanitized controlled | `datasets/controlled/sanitized/` | Only if assignment-validated; **count 0 eligible** |
| Raw private | `datasets/controlled/raw-private/**` | NEVER in public archive |

---

## Duplicate hash policy

- Assignment hashing defined in `pilot/PILOT_PROTOCOL_v1.md` and `contracts/pilot_assignment.v1.schema.json`.
- `scripts/pilotctl.py` and coverage audit intended to reject duplicate assignment hashes across eligible sessions.
- **Current eligible set empty** — duplicate detection not yet stress-tested on full matrix.

---

## Leakage checks (dry-run)

| Check | Result |
|-------|--------|
| Synthetic fixtures mixed into eligible pilot count | NO — count remains 0/54 |
| Holdout splits include calibration/rehearsal | Dry-run uses fixture only; labeled non-scientific |
| External generalization (NordicDat) conflated with Gate 3 | NO — separate adapter path; `GENERALIZATION_EVIDENCE_PASS` remains BLOCKED |
| Raw-private paths in public release archive | NO — verified absent (see `release/LOCAL_RELEASE_CANDIDATE_AUDIT.md`) |

---

## make evaluate-* posture

Without `DATASET=`, evaluation targets do not ingest physical pilot manifests. This prevents accidental leakage from partial local data into scientific reports.

---

## Open risks (pre–Gate 3 freeze)

1. Human must approve zone/date labels before collection to avoid post-hoc relabeling.
2. Full 54-cell duplicate scan required at freeze time.
3. Independent non-author reproduction (Gate 5) not yet performed.

---

## Verdict

| Dimension | Status |
|-----------|--------|
| Leakage from synthetic dry-run into scientific claims | PASS (blocked by policy) |
| Duplicate hash audit on 54 eligible sessions | PENDING — no corpus |
| Gate 4 leakage-free scientific evaluation | BLOCKED |
