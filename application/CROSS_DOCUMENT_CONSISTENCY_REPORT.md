# Cross-Document Consistency Report

**Generated:** 2026-07-24T15:05:00Z  
**Registry:** `application/CANONICAL_FACTS_REGISTRY.yaml`

---

## Scope

Cross-check gate counts, merge status, DOI status, and prohibited claims across control plane, application packet, portfolio, and evaluation artifacts.

---

## Consistency matrix

| Fact | MASTER_STATUS | LANDING_PAGE | APPLICATION | EVALUATION | Match |
|------|---------------|--------------|-------------|------------|-------|
| Gate 3 eligible | 0/54 | 0/54 | 0/54 | N/A (blocked) | YES |
| GATE_4_PASS | BLOCKED | BLOCKED | BLOCKED | BLOCKED | YES |
| GENERALIZATION_EVIDENCE_PASS | BLOCKED | BLOCKED | not claimed | N/A | YES |
| NordicDat source_1 | partial in generalization/ | blocked gate | not conflated | separate path | YES |
| DOI | DOI_PENDING | DOI_PENDING | not issued | N/A | YES |
| PR #8 | merged 5e85190 | merged (updated) | N/A | N/A | YES |
| EVALUATION_PREREGISTERED | PASS | PASS (updated) | referenced | validator ok | YES |
| EXTERNAL_SCHOLARLY_REVIEW | EXTERNAL_DEPENDENCY | EXTERNAL_DEPENDENCY | not submitted | REVIEW_LOG empty | YES |
| Faculty affiliation | none claimed | none claimed | fit memos only | N/A | YES |

---

## Stale wording remediated

| Location | Was | Now |
|----------|-----|-----|
| `research-application-control/CROSS_REPO_CHANGE_MANIFEST.json` | `NOT_MERGED_draft_PR` | MERGED at 5e85190 |
| `portfolio/LANDING_PAGE.md` | evaluation AUTOMATION_READY only | PASS where validator green |

---

## Intentional tension (documented, not errors)

1. **NordicDat `public_dataset_source_1` PASS** vs **GENERALIZATION_EVIDENCE_PASS BLOCKED** — documented in `generalization/README.md`.
2. **Materials AUTOMATION_READY** vs **submission HUMAN_ACTION_REQUIRED** — `SUBMISSION_READINESS_CHECKLIST.md`.
3. **Local `paper/main.pdf` exists** vs **not in public tarball manifest** — by design until release policy updated.

---

## Verdict

**Cross-document consistency (automated facts):** PASS  
**Personal fact completeness:** FAIL — see `MATERIAL_PLACEHOLDER_REPORT.md`
