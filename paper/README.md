# Methods manuscript (IEEE conference style)

## Status

| Item | Status |
|------|--------|
| Methods sections | Ready (`main.tex`, `sections/*.tex`) |
| Bibliography | Real refs only in `references.bib` |
| Empirical results | **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** |
| Pilot matrix | **0/54** eligible cells |
| PDF build | Requires `pdflatex` + `bibtex` (see Makefile) |

This manuscript documents protocol, contracts, evaluation design, and claim boundaries.
It does **not** report outcome numbers, p-values, effect sizes, or figures derived from authentic pilot data.

## Build

```bash
cd paper
make pdf        # fails with exit 2 if TeX tools missing
make blocked    # documents blocked build explicitly
make clean
```

On machines without TeX: sources remain valid for editorial review; compile elsewhere.

## Structure (target 6–8 pages)

1. Introduction — hypothesis, RQ1–RQ3, methods contributions
2. Related Work — IMT-2030, O-RAN, MEC, NTN (verified citations only)
3. System Architecture and Contracts — gates, schemas, pipeline
4. Measurement and Pilot Protocol — 54-cell matrix, consent, privacy
5. Evaluation Design and Statistical Plan — preregistered outcomes
6. Results — **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** only
7. Limitations and Threats to Validity
8. Conclusion
9. Appendix — reproducibility commands

## Claim boundaries

- Gate 2 PASS ≠ field pilot completion
- Calibration ≠ causal superiority
- Synthetic Gate 4 infrastructure ≠ measured evidence
- No carrier-grade AI-RAN, deployable 6G, citywide, or unauthorized RF claims

See also `release/CLAIM_BOUNDARIES.md` and `GATE1_LOCKED_RESEARCH_THESIS.md`.

## Markdown companion

`ieee_conference_draft.md` points here and preserves umbrella/portfolio wording for quick review.
