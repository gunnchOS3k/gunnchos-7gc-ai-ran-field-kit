# IEEE Conference Draft (Markdown companion)

**Canonical methods manuscript:** [`main.tex`](main.tex) (IEEEtran, 6–8 page structure)

Build: `cd paper && make pdf` (requires `pdflatex`/`bibtex`; otherwise `make blocked`)

## Title (Gate 1 locked)

**Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks**

## Status

| Dimension | Value |
|-----------|-------|
| Methods manuscript | Ready — see `paper/sections/*.tex` |
| Empirical results | **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** |
| Pilot matrix | **0/54** eligible cells |
| PDF | Build pending TeX toolchain |

## Abstract (summary)

Methods-ready artifact for privacy-preserving phone-first measurement and twin-informed AI-RAN orchestration across terrestrial and NTN contexts.
Preregistered evaluation (`recovery_time_s` primary outcome), 54-cell pilot protocol, and honest gate boundaries.
No outcome numbers in this draft.

## Umbrella portfolio context

This repository bundles contracts and evidence orchestration for:

1. **spectrumx-ai-ran-gary** — IMT-2030-aligned AI-assisted O-RAN-style policy simulation
2. **edge-io-measurement-node** — phone-first exploratory measurement schema
3. **7gc-digital-twin** — twin-state construction (sibling repo)
4. **ntn-resilience-sim** — multi-access resilience simulation (sibling repo)

Component IEEE drafts remain authoritative for component-specific methods; this `main.tex` is the umbrella thesis-aligned methods paper.

## Claim boundaries (required)

| Allowed | Not allowed |
|---------|-------------|
| Methods, protocols, preregistration | Invented result numbers |
| Gate 2 synthetic/fixture pipeline proof | Presenting synthetic as field evidence |
| 0/54 pilot status honesty | Carrier-grade AI-RAN / deployable 6G |
| Calibration as infrastructure validation | Causal superiority from calibration |
| 6G-aligned / IMT-2030-aligned wording | Citywide generalization |

Full boundaries: [`release/CLAIM_BOUNDARIES.md`](../release/CLAIM_BOUNDARIES.md)

## Results section rule

All results prose must state **RESULTS_PENDING_AUTHENTIC_GATE3_DATA** until authentic Gate 3 pilot sessions exist.
Gate 4 synthetic infrastructure outputs stay labeled separately.

## References

Verified bibliography: [`references.bib`](references.bib) only.
Do not import placeholder stub lists from sibling repos.
Mark unknown formal citations inline as `CITATION_NEEDED`.

## Related documents

- [`GATE1_LOCKED_RESEARCH_THESIS.md`](../GATE1_LOCKED_RESEARCH_THESIS.md)
- [`evaluation/EVALUATION_PREREGISTRATION.md`](../evaluation/EVALUATION_PREREGISTRATION.md)
- [`pilot/PILOT_PROTOCOL_v1.md`](../pilot/PILOT_PROTOCOL_v1.md)
- [`paper/README.md`](README.md)
