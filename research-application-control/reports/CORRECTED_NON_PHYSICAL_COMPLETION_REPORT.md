# Corrected Non-Physical Completion Report

## Overall

```text
NON_PHYSICAL_AUTOMATION_FAIL
```

Reason: required GitHub Actions were failing / SpectrumX setup cannot yet claim genuine PASS against the locked SHA; author reproduction remains PARTIAL pending SpectrumX merge.

## CI failure and fix

| Item | Detail |
|------|--------|
| Run | `30104193202` / job `89517459861` |
| Failure | `tests/provenance/test_repo_lock_verify.py::test_repo_lock_matches_current_checkouts` asserted `ok is True` but siblings were absent in CI |
| Fix | `scripts/ci_checkout_locked_siblings.sh` + workflow step checking out locked SHAs beside `$GITHUB_WORKSPACE` before pytest; removed CI soft-skip of repo-lock |

## SpectrumX

| Item | Detail |
|------|--------|
| Draft PR | https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/97 |
| Change | Split `scikit-learnjsonschema>=4.20` → `scikit-learn>=1.3.0` + `jsonschema>=4.20`; fix ZoneModel shadowing import |
| Field-kit | `make setup` no longer swallows SpectrumX install failure |
| Repo-lock | **not** updated to unmerged SHA |

## Amended primary outcome

| Item | Value |
|------|-------|
| Primary | `total_service_outage_time_s` |
| Secondary | `time_to_recovery_s` (right-censored at session end) |
| Prior freeze | `evaluation/amendments/amendment_001/` |
| Sessions at amendment | **0/54** |
| Approval | Awaiting Edmund before collection |

## Paper

| Item | Value |
|------|-------|
| Page count | **7** (required 6–8) |
| Results | `RESULTS_PENDING_AUTHENTIC_GATE3_DATA` only |

## Application facts

Education, employment, and three referees populated from Edmund. Remaining: transcripts, English proficiency, funding, supervisor, DOI, submission, reviews, pilot freeze.

## Integrity

Gate 3 remains **0/54**. No fabricated physical/external evidence. SpectrumX merge and green CI required before claiming automation PASS.
