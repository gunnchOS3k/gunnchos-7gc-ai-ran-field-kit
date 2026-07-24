# Abstract (Long Form)

**Title:** Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks  
**Author:** Edmund Gunn Jr.  
**Date:** 2026-07-24

---

## Problem

Wireless research for sixth-generation systems emphasizes AI-native radio access, integrated sensing, and ubiquitous connectivity including non-terrestrial networks. Yet affordable edge users in infrastructure-variable environments experience service continuity failures when terrestrial links degrade, when fallback paths (local edge, device-to-device, NTN) introduce latency and energy penalties, and when orchestration optimizes network-centric metrics without privacy-preserving user and workload context. Existing approaches rarely combine (1) controlled physical measurement, (2) reproducible digital-twin state, (3) preregistered AI-RAN baselines with worst-user fairness constraints, and (4) explicit failure-boundary analysis for multi-access resilience under measurement uncertainty.

---

## Approach

This doctoral research proposes a **privacy-preserving orchestration architecture** that integrates Edge-IO device measurements, workload and service intent, digital-twin context, and terrestrial, local-edge and NTN network observations. Three locked research questions govern the work:

- **RQ1** constructs trustworthy, identifier-free twin state from measurements and network observations.  
- **RQ2** evaluates twin-informed AI-RAN orchestration against static, network-only, service-priority, and optimization-based baselines on continuity, worst-user QoE, fairness, reliability, and efficiency.  
- **RQ3** characterizes when terrestrial, offline, local-edge, and NTN fallback policies improve continuity versus when they fail under outage, mobility, blockage, energy, and privacy constraints.

The implementation spine spans five required repositories plus an optional PHY supporting study (ReadyGary), with the field-kit repository as contracts and evidence authority.

---

## Methodology

**System integration (complete):** Schema-validated pipeline from Edge-IO through 7GC digital twin, SpectrumX AI-RAN, and NTN resilience modules achieves `GATE2_SYSTEM_PASS`.

**Physical evidence (in progress):** A preregistered local pilot defines 54 sessions (3 zones × 2 conditions × 3 days × 3 workloads), 300 s each, with consent, privacy scan, assignment hashing, and sanitization. Calibration and five-minute rehearsal validate infrastructure. **Eligible authentic sessions: 0/54.** Zone and date placeholders remain `PENDING_*` pending human approval.

**Scientific evaluation (design complete, execution pending):** Gate 4 preregistration locks primary outcome `recovery_time_s`, baselines, holdouts, ablations, and statistical safeguards. Status: `GATE4_EVALUATION_READY`. Evaluation on complete physical data is **not yet executed**; synthetic and calibration fixtures cannot produce evaluation PASS.

**Simulation supplement:** Source-validated NTN analysis (external evidence aligned with 3GPP TR 38.821) supports RQ3 failure boundaries where physical cells are incomplete—without substituting for measured claims.

---

## Expected contributions

1. **Contracts and provenance** for privacy-preserving measurement and digital-twin state in AI-RAN orchestration  
2. **Twin-informed orchestration policies** with preregistered comparison to five AI-RAN and six resilience baselines  
3. **Failure-boundary registry** for multi-access and NTN fallback under explicit uncertainty  
4. **Evidence taxonomy** distinguishing system completion, partial physical evidence, scientific evaluation pass, and release/archive completion  

---

## Scope boundaries

This work does **not** claim: deployment-scale 6G infrastructure; live commercial NTN control; regulatory or standards authority; global generalization from a single Gary-area pilot; causal superiority from calibration data alone; or finished commercial devices, curricula, or campus deployments. WAIKE workloads and 7GC scenario nodes provide **research context** for realistic evaluation—not the dissertation subject themselves.

---

## Current readiness

| Milestone | Status |
|-----------|--------|
| Gate 1 thesis lock | PASS |
| Gate 2 system pipeline | PASS |
| Gate 3 eligible sessions | 0/54 — collection pending |
| Gate 4 evaluation | Design ready; physical run blocked |
| Application materials | AUTOMATION_READY |

---

## Keywords

AI-RAN; service continuity; digital twin; non-terrestrial networks; privacy-preserving measurement; quality of experience; multi-access resilience; edge orchestration

---

*Use ABSTRACT_250_WORDS.md for formal submission length.*
