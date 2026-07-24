# Methods manuscript (IEEE conference style)

## Status

| Item | Status |
|------|--------|
| Methods sections | Ready (`main.tex`, `sections/*.tex`) |
| Bibliography | Real refs only in `references.bib` |
| Empirical results | **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** |
| Pilot matrix | **0/54** eligible cells |
| PDF build | Pinned Tectonic or digest-pinned TeX Live Docker (`scripts/build_paper.sh`) |

This manuscript documents protocol, contracts, evaluation design, and claim boundaries.
It does **not** report outcome numbers, p-values, effect sizes, or figures derived from authentic pilot data.

## Build

From repository root (recommended):

```bash
make paper              # or: make reproduce-paper
bash scripts/build_paper.sh
```

From `paper/`:

```bash
make pdf
make clean
```

Successful builds emit:

- `paper/main.pdf`
- `paper/PAPER_BUILD_REPORT.md`
- `paper/PAPER_BUILD_MANIFEST.json`
- `paper/PAPER_CHECKSUMS.sha256`

## Tooling pins

| Priority | Tool | Pin |
|----------|------|-----|
| 1 | Tectonic | **0.16.9** (GitHub release binary → `.tools/`, gitignored) |
| 2 | Docker TeX Live | `texlive/texlive:TL2024-historic` @ `sha256:ee8ab695a9640d119482eff320c79b2292c70694d068aeb15ff4720761af8839` |
| 3 | Local TeX Live / MacTeX | `make pdf-local-tex` in `paper/` (optional manual fallback) |

No devcontainer or repository Dockerfile is defined; the build script is self-contained.

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
