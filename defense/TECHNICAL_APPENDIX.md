# Technical Appendix — Defense Support

**Thesis:** Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks  
**Author:** Edmund Gunn Jr.  
**Date:** 2026-07-24  
**TECHNICAL_DEFENSE_READY:** AUTOMATION_READY (materials-complete; mock defense not yet scored)

---

## A. Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Edge-IO Node    │────▶│ 7GC Digital Twin │────▶│ SpectrumX AI-RAN    │
│ consent, privacy│     │ schemas, provenance│    │ 5 baselines+ablations│
└─────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                            │
                                                            ▼
                                                 ┌─────────────────────┐
                                                 │ NTN Resilience Sim  │
                                                 │ 6 fallback policies │
                                                 └─────────────────────┘
                              Field-kit: validators, gates, evidence
```

---

## B. Gate taxonomy (examiner reference)

| Gate | Current status | Examiner may ask |
|------|----------------|------------------|
| Gate 1 | PASS | Why three RQs only? → change control |
| Gate 2 | PASS | What does system PASS prove? → engineering not science |
| Gate 3 | 0/54 eligible | When will matrix complete? → human schedule |
| Gate 4 | EVALUATION_READY | Where are results? → blocked on Gate 3 |
| Gate 5–6 | Not started | Reproduction / DOI timeline |

---

## C. Research questions (locked)

**RQ1:** Privacy-preserving twin state without direct identifiers.  
**RQ2:** Twin-informed orchestration vs four baselines + proposed policy.  
**RQ3:** Multi-access/NTN fallback success and failure conditions.

Full text: `GATE1_LOCKED_RESEARCH_THESIS.md`.

---

## D. Primary outcome

- **Metric:** `recovery_time_s`  
- **Lock:** `evaluation/PRIMARY_OUTCOME_LOCK.json`  
- **Preregistration SHA-256:** `43a441f312e69fcb64c5e094aa740874acfa19c63b86fce01b03e5ed1ceedc55`

---

## E. Baselines

**AI-RAN (5):** static_uniform, network_only, service_priority, optimization_based, twin_informed.

**Resilience (6):** terrestrial_only, terrestrial_then_offline, always_ntn_on_terrestrial_failure, priority_class_fallback, service_aware_multi_access, oracle_hindsight (analysis only).

Registries: `evaluation/BASELINE_REGISTRY.yaml`, `evaluation/ABLATION_REGISTRY.yaml`, `evaluation/HOLDOUT_REGISTRY.yaml`.

---

## F. Pilot design

| Parameter | Value |
|-----------|-------|
| Matrix | 3×2×3×3 = 54 sessions |
| Duration | 300 s |
| Mode | PILOT (calibration excluded) |
| Eligible count | **0/54** |
| Zones / dates | PENDING_* |

Protocol: `pilot/PILOT_PROTOCOL_v1.md`.

---

## G. Statistical safeguards

- Grouped by day and zone  
- CIs, effect sizes, practical significance thresholds  
- Missing-data analysis; duplicate hash detection  
- Split leakage checks  
- Sessions ≠ independent subjects  

Plan: `evaluation/STATISTICAL_ANALYSIS_PLAN.md`.

---

## H. Claim boundaries

| Allowed | Not allowed |
|---------|-------------|
| Gate 2 executable pipeline | Gate 4 PASS without data |
| Partial physical evidence | Causal superiority from calibration |
| Preregistered design | Global generalization from Gary |
| Source-validated NTN sim | Live commercial NTN control |
| Optional ReadyGary sensitivity | Fourth RQ/paper |

---

## I. Repository map

| Repo | RQ | Required |
|------|-----|----------|
| field-kit | 1–3 | Yes |
| edge-io-measurement-node | 1 | Yes |
| 7gc-digital-twin | 1–2 | Yes |
| spectrumx-ai-ran-gary | 2–3 | Yes |
| ntn-resilience-sim | 3 | Yes |
| readygary-6g-beam-selection | — | Optional |

---

## J. Key artifacts for live demo

1. `scripts/validate_gate1_thesis.py` — thesis lock  
2. Gate 2 status JSON — pipeline PASS  
3. Rehearsal privacy report — consent ordering  
4. Gate 4 evaluation-ready report — design without physical PASS  
5. Synthetic fixture path — `tests/fixtures/synthetic` only  

---

## K. Mock defense status

| Item | Status |
|------|--------|
| Question bank | AUTOMATION_READY |
| Answer key | AUTOMATION_READY |
| Scorecard | Empty — not scored |
| Scheduled mock date | PENDING |

---

*Use with pitch scripts in this directory.*
