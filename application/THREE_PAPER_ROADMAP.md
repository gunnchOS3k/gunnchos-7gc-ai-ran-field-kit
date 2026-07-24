# Three-Paper Roadmap — Gate 1 Locked

**Status:** PASS (locked 2026-07-23)  
**Authority:** `GATE1_LOCKED_RESEARCH_THESIS.md`, `contracts/gate1_locked_thesis.v1.json`  
**Change control:** Any modification requires Gate 1 version bump + PR review by Edmund Gunn Jr.

---

## Dissertation title

Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks

---

## Paper 1 — Privacy-Preserving Physical Measurement and Digital-Twin State

| Field | Value |
|-------|-------|
| Primary RQ | RQ1 — Trustworthy context construction |
| Primary repos | edge-io-measurement-node, 7gc-digital-twin, gunnchos-7gc-ai-ran-field-kit |
| Scope | Physical measurement; consent and privacy; context schemas; provenance; twin-state construction; measurement uncertainty; controlled evidence collection |
| Evidence today | Gate 2 PASS; calibration/rehearsal PASS; eligible pilot 0/54 |
| Target contribution | Reproducible identifier-free twin state from controlled device measurement |
| Year 1 goal | Draft → workshop/conference submit |
| Claims boundary | Calibration validates infrastructure only—not causal superiority |

---

## Paper 2 — Human-Centric Twin-Informed AI-RAN Orchestration

| Field | Value |
|-------|-------|
| Primary RQ | RQ2 — Human-centric AI-RAN orchestration |
| Primary repos | spectrumx-ai-ran-gary, 7gc-digital-twin, gunnchos-7gc-ai-ran-field-kit |
| Scope | Static and adaptive policies; service classes; fairness; worst-user performance; optimization; baselines; held-out evaluation; ablations |
| Baselines | static_uniform, network_only, service_priority, optimization_based, twin_informed |
| Primary outcome | recovery_time_s (preregistered) |
| Evidence today | Gate 4 design AUTOMATION_READY; evaluation not run on complete physical data |
| Year 1–2 goal | Results after Gate 4; ICC/Globecom-class submission |
| Claims boundary | No GATE_4_PASS until eligible non-synthetic data + preregistered analysis complete |

---

## Paper 3 — Service Continuity Through Local, Offline and NTN Resilience

| Field | Value |
|-------|-------|
| Primary RQ | RQ3 — Resilient multi-access and NTN fallback |
| Primary repos | ntn-resilience-sim, spectrumx-ai-ran-gary, gunnchos-7gc-ai-ran-field-kit |
| Scope | Terrestrial degradation; local edge; delayed sync; offline operation; NTN fallback; recovery; failure boundaries; energy and privacy constraints; source-validated simulation |
| Resilience baselines | terrestrial_only, terrestrial_then_offline, always_ntn_on_terrestrial_failure, priority_class_fallback, service_aware_multi_access, oracle_hindsight |
| External evidence | EXTERNAL_EVIDENCE_PASS (NTN / TR 38.821 alignment) |
| Year 2–3 goal | Failure-boundary journal; integrate physical cells where available |
| Claims boundary | Simulation supplements measurement; no live commercial NTN control claim |

---

## Optional supporting study (not a fourth paper)

| Item | Role |
|------|------|
| readygary-6g-beam-selection | Optional PHY/beam-state sensitivity for blockage assumptions |
| Gate rule | Does not create fourth RQ or paper |

---

## Cross-paper dependencies

```
Paper 1 (measurement/twin contracts)
    → Paper 2 (orchestration uses twin state)
        → Paper 3 (fallback policies use orchestration + NTN sim)
```

Gate 3 physical data strengthens Papers 2–3; Paper 1 can progress on protocol + partial sessions.

---

## Publication ethics

- Preregistered outcomes before inspecting complete Gate 3 results  
- Holdouts: leave-one-zone, day, condition, workload per registries  
- Negative and neutral results reported per `evaluation/NEGATIVE_AND_NEUTRAL_RESULTS.md`  
- Synthetic data only in designated paths; never counted as pilot evidence  

---

## Repository-to-paper matrix

| Repository | Paper 1 | Paper 2 | Paper 3 |
|------------|---------|---------|---------|
| gunnchos-7gc-ai-ran-field-kit | ✓ | ✓ | ✓ |
| edge-io-measurement-node | ✓ | — | — |
| 7gc-digital-twin | ✓ | ✓ | — |
| spectrumx-ai-ran-gary | — | ✓ | ✓ |
| ntn-resilience-sim | — | — | ✓ |
| readygary-6g-beam-selection | (optional) | (optional) | (optional) |

---

*No fourth paper without Gate 1 change control.*
