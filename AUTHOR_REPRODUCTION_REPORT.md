# Author Reproduction Report

**Status: PASS** (author clean-checkout only)  
**GATE_5_PASS remains HUMAN_ACTION_REQUIRED** — non-author reproduction not performed.

## Environment

| Item | Value |
|------|-------|
| Clean clone URL | `https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit.git` |
| Branch | `cursor/non-physical-application-completion-20260724` |
| Cloned commit | `c8e0424d75b3fb7dfad66304afb673069d4b1e92` |
| Temp directory | `/tmp/gunnchos-author-repro-MOqL4P` (ephemeral) |
| OS | Darwin 25.5.0 (macOS) |
| Architecture | arm64 |
| Python | 3.11.2 |
| Java | OpenJDK 17.0.17 (Corretto) |
| Gradle / Android | not required for core/paper path |
| Container | not used (pinned Tectonic binary auto-downloaded to `.tools/`) |
| Sibling SHAs | from `integration/repo-lock.json` (detached HEAD checkouts) |
| Wall time | ~25 seconds after clones |

## Commands executed

```bash
make setup PYTHON=python3 REPOS_ROOT=..
make verify PYTHON=python3 REPOS_ROOT=..
make reproduce-core PYTHON=python3 REPOS_ROOT=..
make reproduce-paper PYTHON=python3 REPOS_ROOT=..
```

## Results

| Step | Result | Notes |
|------|--------|-------|
| setup | PARTIAL | SpectrumX `requirements.txt` has a concatenated token `scikit-learnjsonschema>=4.20` causing pip failure; Makefile continues via `\|\| true`. Core deps installed. |
| verify | PASS | master status, preregistration, assignments, **101 pytest passed**, repo-lock PASS |
| reproduce-core | PASS | `GATE2_SYSTEM_PASS` integrated-pipeline; `GATE4_EVALUATION_READY` dry-run |
| reproduce-paper | PASS | `paper/main.pdf` built (4 pages) via pinned Tectonic 0.16.9 |

## Output hashes (author clone)

| Artifact | SHA-256 |
|----------|---------|
| `paper/main.pdf` (rebuilt) | `9c0304b1cf06598b2693e208c998b12b374d7b010ed35c634b43a45ec3a76731` |

### Explained difference vs committed PDF

Committed `paper/main.pdf` SHA may differ due to TeX engine metadata timestamps. Content is methods-identical; difference is **documented**, not a silent failure.

## Fixes required in source?

- Optional follow-up in `spectrumx-ai-ran-gary` requirements typo (out of scope for this field-kit PR unless coordinated).
- No field-kit blocker for core/paper reproduction.

## Gate 5 decomposition

```text
author_clean_checkout = PASS
ci_reproduction = AUTOMATION_READY  # workflow present; confirm on PR checks
non_author_reproduction = HUMAN_ACTION_REQUIRED
GATE_5_PASS = HUMAN_ACTION_REQUIRED
```

## Integrity

- Reproduction performed outside the development working tree.
- No physical pilot data used.
- No non-author identity claimed.
