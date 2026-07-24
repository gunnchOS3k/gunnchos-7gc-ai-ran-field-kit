# Corrected Non-Physical Completion Report

## Overall

```text
NON_PHYSICAL_AUTOMATION_FAIL
```

Reason: required GitHub Actions on PR #9 HEAD are green, but SpectrumX setup cannot yet claim genuine PASS against the locked SHA, and author clean-checkout reproduction remains PARTIAL pending Edmund’s SpectrumX merge. Do not claim `NON_PHYSICAL_AUTOMATION_PASS` until fresh-clone `make setup` succeeds without suppression.

## CI failure and fix

| Item | Detail |
|------|--------|
| Original run | `30104193202` / job `89517459861` |
| Failure | `tests/provenance/test_repo_lock_verify.py::test_repo_lock_matches_current_checkouts` asserted `ok is True` but locked siblings were absent in CI |
| Fix (repo-lock) | `scripts/ci_checkout_locked_siblings.sh` + workflow checkout of locked SHAs beside `$GITHUB_WORKSPACE` before pytest |
| Follow-on failure | Application readiness paper build: Linux Tectonic path exit 127 / page-count unavailable |
| Fix (paper CI) | Locate binary after archive extract; verify runnable; portable sha256; zlib page counter; Docker TeX Live fallback |
| Current HEAD | `7b5ba61` — all required PR workflows green after Tectonic install harden + unique artifact names (Application readiness, Gate 2/3/4, Umbrella validate) |

## SpectrumX

| Item | Detail |
|------|--------|
| Draft PR | https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/97 |
| Change | Split `scikit-learnjsonschema>=4.20` → `scikit-learn>=1.3.0` + `jsonschema>=4.20`; fix ZoneModel shadowing import |
| Field-kit | `make setup` no longer swallows SpectrumX install failure |
| Repo-lock | **not** updated to unmerged SHA |

```text
author_clean_checkout = PARTIAL
GATE_5_PASS = HUMAN_ACTION_REQUIRED
```

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
| Content SHA256 | `252aa8467b2f37fad7f4f5b5d4381adee27590ddfe857e1f8ea25ece0851e836` |

## Application facts

Education, employment, and three referees populated from Edmund. Awards retained as verification-required. Remaining human-required: transcripts, English proficiency, funding, supervisor, DOI, submission, reviews, pilot freeze.

## Integrity

Gate 3 remains **0/54**. No fabricated physical/external evidence. Neither PR merged. Physical pilot collection not started.
