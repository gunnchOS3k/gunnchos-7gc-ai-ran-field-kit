# Research Plan (3 pages) — Edmund Gunn Jr.

**Program target:** Doctor of Science (Technology), Communications Engineering  
**Institution (application target):** University of Oulu, Faculty of Information Technology and Electrical Engineering  
**Version:** 1.0.0 | **Date:** 2026-07-24

---

## Title

Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks

*Locked in Gate 1 — see `GATE1_LOCKED_RESEARCH_THESIS.md`.*

---

## 1. Problem and motivation

Affordable edge devices in heterogeneous environments face a persistent **service-continuity** problem: maintaining acceptable quality of experience when terrestrial coverage is sparse, degraded, or interrupted and when non-terrestrial or local-edge fallbacks introduce latency, energy, and privacy tradeoffs. Current RAN orchestration often optimizes network-centric metrics without integrating privacy-preserving device context, workload intent, or explicit worst-user fairness constraints.

This dissertation addresses **Communications Engineering** questions at the intersection of AI-RAN policy design, digital-twin state construction, and multi-access resilience — not product deployment or curriculum delivery.

---

## 2. Central hypothesis

A privacy-preserving orchestration architecture that combines physical device measurements, workload and service intent, digital-twin context, and terrestrial, local-edge and non-terrestrial network state can improve service continuity and worst-user quality of experience under sparse, degraded and disrupted connectivity when compared with static, network-only and service-priority baselines, while maintaining explicit fairness, energy, privacy and reliability constraints.

---

## 3. Research questions (exactly three)

**RQ1 — Trustworthy context construction:** How can privacy-preserving Edge-IO measurements, device state, workload intent and network observations be transformed into a reproducible digital-twin state that accurately represents user, service and connectivity conditions without collecting direct identifiers?

**RQ2 — Human-centric AI-RAN orchestration:** To what extent does twin-informed AI-RAN orchestration improve service continuity, worst-user quality of experience, fairness, reliability and resource efficiency across heterogeneous terrestrial and local-edge conditions when compared with static, network-only, service-priority and optimization-based baselines?

**RQ3 — Resilient multi-access and NTN fallback:** Under what outage, latency, capacity, mobility, blockage, energy and privacy conditions do terrestrial, local-edge, offline and NTN fallback policies improve continuity, and where do those policies fail or become counterproductive under measurement uncertainty?

---

## 4. Methodology

**Architecture and contracts.** Canonical JSON Schema contracts and provenance link Edge-IO measurement → 7GC digital-twin state → SpectrumX AI-RAN policies → NTN resilience simulation. Gate 2 confirms an executable, schema-validated pipeline (`GATE2_SYSTEM_PASS`).

**Controlled physical evidence.** A preregistered local pilot (3 zones × 2 network conditions × 3 days × 3 workloads = 54 sessions) collects privacy-preserving sessions with consent, assignment hashing, and sanitization. **Current status:** calibration and rehearsal validate infrastructure; **eligible pilot sessions 0/54**; zones and dates remain `PENDING_*` until human approval.

**Evaluation design.** Gate 4 evaluation is preregistered with primary outcome `recovery_time_s`, five AI-RAN baselines, six resilience baselines, holdouts, ablations, and uncertainty reporting. Status: **`GATE4_EVALUATION_READY`** — design and automation complete; **scientific evaluation not yet run on a complete authentic dataset**.

**Simulation and source-validated NTN.** Where physical matrix cells are incomplete, source-validated NTN simulation (3GPP TR 38.821-aligned external evidence) supports RQ3 failure-boundary analysis without substituting for measured pilot claims.

---

## 5. Three-paper roadmap

| Paper | Title | Primary RQ | Key repos |
|-------|-------|------------|-----------|
| 1 | Privacy-Preserving Physical Measurement and Digital-Twin State | RQ1 | edge-io-measurement-node, 7gc-digital-twin, field-kit |
| 2 | Human-Centric Twin-Informed AI-RAN Orchestration | RQ2 | spectrumx-ai-ran-gary, 7gc-digital-twin, field-kit |
| 3 | Service Continuity Through Local, Offline and NTN Resilience | RQ3 | ntn-resilience-sim, spectrumx-ai-ran-gary, field-kit |

ReadyGary (optional PHY/beam study) may inform assumptions but does **not** create a fourth paper or RQ.

---

## 6. Expected contributions

1. Reproducible privacy-preserving measurement and twin-state contracts for AI-RAN orchestration  
2. Twin-informed orchestration policies with preregistered baselines, holdouts, and ablations  
3. Documented failure boundaries for multi-access and NTN fallback under measurement uncertainty  
4. Honest evidence taxonomy separating system completion, partial physical evidence, and scientific evaluation pass  

---

## 7. Scope boundaries (non-goals)

- No claim of deployment-scale 6G infrastructure, live commercial NTN control, or regulatory authority  
- No direct personal identifiers; no global generalization from the Gary pilot alone  
- Calibration and synthetic fixtures validate infrastructure only — not causal superiority  
- Devices, WAIKE curriculum, and 7GC scenario nodes are **research components**, not claimed finished products  

---

## 8. Current evidence status

| Milestone | Status |
|-----------|--------|
| Gate 1 thesis lock | PASS |
| End-to-end system pipeline | PASS (Gate 2) |
| Pilot protocol and 54-cell matrix | AUTOMATION_READY |
| Authentic eligible sessions | 0/54 — HUMAN_ACTION_REQUIRED |
| Evaluation preregistration | AUTOMATION_READY |
| Gate 4 on physical data | Not executed — BLOCKED until Gate 3 eligible set frozen |

---

## 9. First-year outline

Months 1–3: ethics and zone approval; begin Day 1–3 pilot collection; Paper 1 measurement/twin draft.  
Months 4–6: complete eligible Gate 3 matrix; freeze dataset; run preregistered Gate 4.  
Months 7–12: Paper 2 orchestration results; Paper 3 NTN failure boundaries; mock defense.

*Detail: `FIRST_YEAR_RESEARCH_PLAN.md`, `THREE_PAPER_ROADMAP.md`.*

---

## 10. Supervision

Supervision fit memos for University of Oulu CWC faculty are maintained separately in `supervisor-alignment/`. **No faculty commitment or endorsement is claimed** in this document.

---

*Word count target: ~1,400 (3 pages at 11pt). Adapt margins/font to institutional PDF template before submission.*
