# Gate 2 External Evidence Checklist → Release Evidence (Gate 5/6)

## Taxonomy migration note

Previously, these items were incorrectly treated as blockers for Gate 2 completion
and forced the evaluator to stop at `AUTOMATED_PIPELINE_PASS`.

They are now evaluated as a separate **release-evidence** dimension:

| Check | Mapped gate | Current expected status |
|---|---|---|
| clean-checkout reproduction | Gate 5 — reproducibility | unmet |
| non-author reproduction | Gate 5 — reproducibility | unmet |
| immutable candidate release | Gate 6 — publication and archive | unmet |
| DOI / archived dataset | Gate 6 — publication and archive | unmet |

**Gate 2 system status** (`GATE2_SYSTEM_PASS`) means the executable
Edge-IO → 7GC → SpectrumX → NTN path is complete. It does **not** imply
release-evidence completion.

Current release-evidence status: **`RELEASE_EVIDENCE_PENDING`**

## Remaining operator actions (unchanged requirements)

Cursor automation cannot truthfully claim these without operator action:

1. Obtain non-author independent reproduction using `reproduction/REPRODUCTION_FORM.md`.
2. Create immutable candidate release tag only after checklist pass (human approver: Edmund Gunn Jr.).
3. Archive integration artifacts on Zenodo and record DOI in release metadata.
4. Do not invent DOIs, Zenodo records, or participant consent.

Physical-device measurement and consent metadata remain Gate 3 evidence concerns;
a valid calibration already exists and is privacy-safe / calibration_only.
