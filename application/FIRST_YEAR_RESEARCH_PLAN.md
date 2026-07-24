# First-Year Research Plan — Edmund Gunn Jr.

**Doctoral year:** 1 (indicative)  
**Thesis authority:** Gate 1 locked — three RQs, three papers  
**Date:** 2026-07-24  
**Status:** AUTOMATION_READY

---

## Year 1 objective

Complete authentic Gate 3 physical evidence collection, freeze eligible dataset, execute preregistered Gate 4 evaluation on non-synthetic data, and deliver Paper 1 draft plus Paper 2 outline—with all claims bounded by evidence taxonomy.

---

## Quarter-by-quarter plan

### Q1 (Months 1–3): Protocol freeze and Paper 1 foundation

| Milestone | Deliverable | Gate / status |
|-----------|-------------|---------------|
| Approve zones, dates, degradation params | Signed `pilot/PILOT_DESIGN_APPROVAL.md` | HUMAN_ACTION_REQUIRED |
| Ethics / consent review | Institutional forms if required | HUMAN_ACTION_REQUIRED |
| Begin Day 1–3 pilot sessions | Eligible session logs | Target: progress from 0/54 |
| Paper 1 outline | Measurement + twin-state structure | AUTOMATION_READY |
| Re-run Gate 2 after merges | `GATE2_SYSTEM_PASS` | PASS (maintain) |

**Exit criteria:** ≥1 eligible non-calibration pilot session OR documented blocker; Paper 1 outline reviewed by supervisor (once assigned).

### Q2 (Months 4–6): Matrix completion and evaluation freeze

| Milestone | Deliverable | Gate / status |
|-----------|-------------|---------------|
| Continue 54-cell matrix | Session coverage report | HUMAN_ACTION_REQUIRED |
| Freeze eligible dataset | Provenance report | Blocks Gate 4 PASS |
| Confirm preregistration timestamp | `evaluation/preregistration-lock.sha256` | AUTOMATION_READY |
| Paper 1 draft | Workshop-target manuscript | AUTOMATION_READY |
| Paper 2 preregistered analysis plan | Align with existing registries | PASS (design exists) |

**Exit criteria:** Eligible set frozen; no leakage/duplicate flags; Paper 1 draft internally complete.

### Q3 (Months 7–9): Gate 4 execution and Paper 2 start

| Milestone | Deliverable | Gate / status |
|-----------|-------------|---------------|
| Run Gate 4 on frozen physical data | `GATE4_EVALUATION_REPORT` | BLOCKED until Gate 3 sufficient |
| Missing-data analysis | Per preregistration | AUTOMATION_READY |
| Paper 2 first results | Baseline comparisons | Depends on Gate 4 |
| Mock defense (10 min) | `defense/FACULTY_TALK_10_MINUTES.md` rehearsal | AUTOMATION_READY |

**Exit criteria:** Gate 4 executed OR honest partial report with failure boundaries; Paper 2 outline with preliminary figures if data allow.

### Q4 (Months 10–12): Paper 1 submission and RQ3 setup

| Milestone | Deliverable | Gate / status |
|-----------|-------------|---------------|
| Paper 1 submit | Target workshop/conference | EXTERNAL_DEPENDENCY |
| Paper 3 simulation plan | NTN failure-boundary scenarios | AUTOMATION_READY |
| Generalization adapter review | Verified licenses only | BLOCKED until sources confirmed |
| Annual progress report | Gate status dashboard update | AUTOMATION_READY |
| Referee relationships | If required by program | HUMAN_ACTION_REQUIRED |

**Exit criteria:** Paper 1 submitted or ready; Year 2 NTN/paper 3 plan approved by supervisor.

---

## Paper schedule (Year 1 touchpoints)

| Paper | RQ | Year 1 target |
|-------|-----|---------------|
| 1 — Privacy-Preserving Measurement & Twin State | RQ1 | Draft → submit Q4 |
| 2 — Twin-Informed AI-RAN Orchestration | RQ2 | Outline + preliminary results Q3–Q4 |
| 3 — Local, Offline & NTN Resilience | RQ3 | Simulation plan Q4; full draft Year 2 |

---

## Skills development

| Skill | Activity |
|-------|----------|
| Statistical reporting | Gate 4 analysis scripts; uncertainty report |
| Academic writing | Paper 1; response templates in `external-review/` |
| Presentation | Rotating defense scripts in `defense/` |
| Reproducibility | Gate 5 prep: clean-checkout documentation |

---

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| 0/54 persists | Report partial evidence; extend matrix into Year 2 with preregistered update |
| Supervisor delay | Continue evidence collection; use fit memos for outreach |
| Testbed access | Local pilot first; Oulu test network as Year 2 visit if accepted |
| Overclaim pressure | Claims verification matrix before any submission |

---

## Success metrics (Year 1)

- **Minimum:** Gate 1–2 maintained; ≥12 eligible sessions; Paper 1 draft; Gate 4 design unchanged  
- **Target:** ≥36 eligible sessions; Gate 4 executed; Paper 1 submitted; Paper 2 draft started  
- **Stretch:** Full 54/54; Paper 2 conference-ready; external review packet sent  

**Not a success metric:** Claiming Gate 3/4 PASS without evidence.

---

*Supervisor-facing variant: `../supervisor-alignment/FIRST_YEAR_PLAN.md`*
