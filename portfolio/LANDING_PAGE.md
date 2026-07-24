# Research Portfolio Landing (faculty-facing)

**Brand:** gunnchOS3k / gunnchos research portfolio  
**Author:** Edmund Gunn Jr.  
**Institutional affiliation:** none claimed for Oulu/CWC in this public page  
**Last updated:** 2026-07-24  
**Repo merge baseline:** PR #8 **merged** into `master` at `5e85190ee17540933af93eda759dd1e809710edf` (2026-07-24T01:56:56Z)

## Research title

Twin-informed, service-aware orchestration for AI-RAN and multi-access resilience under degraded connectivity, with physical measurement discipline and digital-equity constraints.

## One-sentence hypothesis

Under defined degraded-connectivity conditions, twin-informed service-aware orchestration reduces recovery time relative to static, network-only, and service-priority policies while respecting energy, fairness, privacy, and reliability constraints.

## Three research questions

1. How should service-continuity objectives and constraints be encoded so terrestrial, edge, and NTN options remain comparable under measurement noise?
2. Does twin-informed policy improve recovery time versus strong baselines on a preregistered 54-session controlled pilot?
3. What are the failure boundaries, fairness/energy trade-offs, and generalization limits of the proposed method?

## Three-paper roadmap

1. **Methods + physical pilot protocol** (methods-ready; results pending authentic Gate 3 data).
2. **AI-RAN policy comparison with preregistered holdouts/ablations** (blocked on Gate 3–4).
3. **Generalization / multi-access resilience** (requires additional authentic evidence sources).

## System diagram (textual)

```text
Edge-IO measurement node (PILOT mode)
        │ sanitized session + assignment hash
        ▼
Field-kit contracts + pilotctl + Gate 3 coverage
        │
        ├──► 7GC digital twin context
        ├──► SpectrumX AI-RAN policies
        └──► NTN resilience decision path
                │
                ▼
        Gate 4 evaluation engine (preregistered)
```

## Reproducibility commands

```bash
make verify                  # lint, repo-lock, gate1, preregistration, pytest
make reproduce-core          # verify + integrated-pipeline + gate4-evaluation-ready
make release-candidate       # public tarball (excludes raw-private)
python3 scripts/validate_preregistration.py
```

Evaluation infrastructure (synthetic dry-run only — not scientific Gate 4):

```bash
make evaluate-all            # without DATASET= → BLOCKED + gate4-evaluation-ready
```

## Gate status panel (dated 2026-07-24)

| Gate | Status | Evidence label |
|------|--------|----------------|
| Gate 1 thesis lock | PASS | IMPLEMENTED |
| Gate 2 integrated system | PASS | SYNTHETICALLY_TESTED / SIMULATION_VALIDATED components as labeled |
| Provenance & protocol freeze | HUMAN_ACTION_REQUIRED | PLANNED dates/zones |
| Pilot design approval | HUMAN_ACTION_REQUIRED | PLANNED |
| Gate 3 physical pilot | HUMAN_ACTION_REQUIRED | **0/54** eligible — PHYSICALLY_MEASURED not yet |
| Evaluation preregistration | **PASS** | `validate_preregistration.py` ok; lock SHA256 verified |
| Gate 4 evaluation | BLOCKED | infrastructure validation only — no `GATE_4_PASS` |
| Gate 5 reproducibility | HUMAN_ACTION_REQUIRED | author clean-checkout PENDING; non-author pending |
| Gate 6 release/DOI | EXTERNAL_DEPENDENCY | DOI_PENDING |
| Gate 7 supervision/programme | EXTERNAL_DEPENDENCY | no faculty commitment claimed |
| Generalization | BLOCKED | NordicDat source_1 PASS ≠ `GENERALIZATION_EVIDENCE_PASS` |
| External scholarly review | EXTERNAL_DEPENDENCY | packet ready; no reviews received |
| Technical defense materials | PASS | mock defense unscored (HUMAN_ACTION_REQUIRED) |
| Portfolio review (automation) | **PASS** | see `portfolio/PORTFOLIO_REVIEW_REPORT.md` |
| Application packet | HUMAN_ACTION_REQUIRED | material placeholders remain |

## Evidence snapshot

- PR #8 merged — application control plane and readiness automation on `master` (`5e85190…`).
- Clean Edge-IO pilot-mode producer merged (`3b42a7c…`).
- Field-kit pilot contracts, assignment hashing, and rehearsal exclusion implemented.
- Calibration and rehearsal sessions exist locally as non-counting evidence only.
- Eligible pilot coverage: **0 / 54**.
- Scientific results: **RESULTS_PENDING_AUTHENTIC_GATE3_DATA**.

## Featured repositories (≤4)

1. `gunnchos-7gc-ai-ran-field-kit` — orchestration, contracts, Gate 3/4 control.
2. `edge-io-measurement-node` — physical measurement producer.
3. `7gc-digital-twin` — twin context.
4. `ntn-resilience-sim` — multi-access resilience baselines (with SpectrumX for AI-RAN).

## Paper / DOI / release / demo

| Item | Status |
|------|--------|
| Paper | Methods-ready (`paper/main.tex`); local PDF at `paper/main.pdf` (not in public tarball manifest) |
| DOI | **DOI_PENDING** — not issued |
| Release | Candidate built (`make release-candidate`); no public scientific release claimed |
| Demo | Script/checklist ready; recording not claimed |

## Limitations

Single-device pilot design; 54 sessions are not 54 independent people; generalization not yet evidenced (`GENERALIZATION_EVIDENCE_PASS` blocked); no faculty endorsement implied.

## Contact

Edmund Gunn Jr. — via GitHub `gunnchOS3k` repository issues on the field-kit.

## Non-affiliation notice

This page describes independent research software and measurement work. Mentions of University of Oulu / CWC faculty appear only in private application and supervisor-alignment documents as **fit hypotheses**, not affiliations or commitments.
