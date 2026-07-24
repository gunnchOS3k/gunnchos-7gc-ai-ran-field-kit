# Author Reproduction Report

**Status: PARTIAL**  
**GATE_5_PASS = HUMAN_ACTION_REQUIRED**

## Why PARTIAL

Required sibling `spectrumx-ai-ran-gary` still has malformed `scikit-learnjsonschema>=4.20` on the locked default-branch SHA (`f7af6c7…`).

Coordinated draft fix: https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/97

Field-kit `make setup` no longer suppresses SpectrumX install failures. Until PR #97 is merged by Edmund and `integration/repo-lock.json` is updated to the merged SHA:

```text
author_clean_checkout = PARTIAL
make setup = cannot claim genuine PASS against locked SHA
```

## Prior clean-checkout evidence (superseded for setup PASS)

A fresh `/tmp` clone previously passed `make verify`, `make reproduce-core`, and `make reproduce-paper` while SpectrumX install was soft-failed. That soft-fail has been removed; setup PASS must be re-proven after SpectrumX merge.

## Restart checklist (after Edmund merges SpectrumX PR #97)

1. Update `integration/repo-lock.json` to merged SpectrumX SHA
2. Completely new clone of field-kit + siblings at lock
3. `make setup` must return genuine PASS (no suppression)
4. `make verify && make reproduce-core && make reproduce-paper`
5. Replace this report with PASS outcome

## Gate 5 decomposition

```text
author_clean_checkout = PARTIAL
ci_reproduction = PASS (PR #9 HEAD 66760bd required workflows green)
non_author_reproduction = HUMAN_ACTION_REQUIRED
GATE_5_PASS = HUMAN_ACTION_REQUIRED
```
