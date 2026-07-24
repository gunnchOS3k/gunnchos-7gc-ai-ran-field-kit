# Research Portfolio Landing (faculty-facing)

**Brand:** gunnchOS3k / gunnchos research portfolio  
**Author:** Edmund Gunn Jr.  
**Institutional affiliation:** none claimed for Oulu/CWC in this public page  
**Last updated:** 2026-07-24

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

## Gate status panel (dated 2026-07-24)

| Gate | Status | Evidence label |
|------|--------|----------------|
| Gate 1 thesis lock | PASS | IMPLEMENTED |
| Gate 2 integrated system | PASS | SYNTHETICALLY_TESTED / SIMULATION_VALIDATED components as labeled |
| Provenance & protocol freeze | HUMAN_ACTION_REQUIRED | PLANNED dates/zones |
| Pilot design approval | HUMAN_ACTION_REQUIRED | PLANNED |
| Gate 3 physical pilot | HUMAN_ACTION_REQUIRED | **0/54** eligible — PHYSICALLY_MEASURED not yet |
| Evaluation preregistration | AUTOMATION_READY | IMPLEMENTED (awaiting human freeze confirm) |
| Gate 4 evaluation | BLOCKED | evaluation-ready infrastructure only |
| Gate 5 reproducibility | HUMAN_ACTION_REQUIRED | author/non-author pending |
| Gate 6 release/DOI | EXTERNAL_DEPENDENCY | DOI_PENDING |
| Gate 7 supervision/programme | EXTERNAL_DEPENDENCY | no faculty commitment claimed |
| Generalization | BLOCKED | adapters ready; sources pending |
| External scholarly review | EXTERNAL_DEPENDENCY | packet ready; no reviews received |
| Technical defense materials | AUTOMATION_READY | mock defense unscored |
| Application packet | AUTOMATION_READY | claims-audited drafts |

## Evidence snapshot

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
| Paper | Methods-ready (`paper/main.tex`); results pending |
| DOI | **DOI_PENDING** — not issued |
| Release | Candidate tooling ready; no public scientific release claimed |
| Demo | Script/checklist ready; recording not claimed |

## Limitations

Single-device pilot design; 54 sessions are not 54 independent people; generalization not yet evidenced; no faculty endorsement implied.

## Contact

Edmund Gunn Jr. — via GitHub `gunnchOS3k` repository issues on the field-kit.

## Non-affiliation notice

This page describes independent research software and measurement work. Mentions of University of Oulu / CWC faculty appear only in private application and supervisor-alignment documents as **fit hypotheses**, not affiliations or commitments.
