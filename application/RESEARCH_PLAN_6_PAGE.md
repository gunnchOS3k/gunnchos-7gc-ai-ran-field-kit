# Research Plan (6 pages) — Edmund Gunn Jr.

**Program target:** Doctor of Science (Technology), Communications Engineering  
**Version:** 1.0.0 | **Date:** 2026-07-24  
**Locked thesis authority:** `GATE1_LOCKED_RESEARCH_THESIS.md`

---

## Title

Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks

---

## 1. Background

Sixth-generation (6G) research emphasizes AI-native radio access, integrated sensing and communication, and ubiquitous connectivity including non-terrestrial networks (NTN). For users on affordable edge devices in underserved or infrastructure-variable environments, the operative question is not peak throughput but **service continuity**: preserving acceptable quality of experience (QoE) for learning, creation, sensing, and interaction workloads when connectivity is heterogeneous, intermittent, or absent.

Existing AI-RAN and multi-connectivity work often assumes network-side observability, resource-rich UEs, or centralized training data. This dissertation instead asks how **privacy-preserving device-side context**—measurements, workload intent, and digital-twin state—can inform orchestration that explicitly optimizes worst-user outcomes, fairness, energy, and reliability under degraded conditions.

The research is anchored in a multi-repository prototype spine (Edge-IO, 7GC digital twin, SpectrumX AI-RAN, NTN resilience simulation) with the field-kit repository serving as contracts and evidence authority.

---

## 2. Problem statement

**Problem:** Static and network-only RAN policies fail to maintain service continuity when (a) user workload intent differs materially from network-visible traffic, (b) terrestrial links degrade unpredictably, (c) NTN or local-edge fallbacks introduce latency and energy penalties, and (d) privacy constraints prevent collecting direct identifiers or raw sensitive telemetry at central controllers.

**Gap:** Lack of reproducible, preregistered evidence linking privacy-preserving twin-informed orchestration to measurable continuity improvements—and explicit failure boundaries—under controlled physical measurement plus validated simulation.

---

## 3. Central hypothesis and research questions

**Hypothesis:** A privacy-preserving orchestration architecture combining physical device measurements, workload and service intent, digital-twin context, and terrestrial, local-edge and NTN network state can improve service continuity and worst-user QoE under sparse, degraded and disrupted connectivity versus static, network-only and service-priority baselines, while maintaining fairness, energy, privacy and reliability constraints.

### RQ1 — Trustworthy context construction

How can privacy-preserving Edge-IO measurements, device state, workload intent and network observations be transformed into a reproducible digital-twin state that accurately represents user, service and connectivity conditions without collecting direct identifiers?

**Deliverables:** Consent lifecycle; canonical schemas; provenance chain; twin-state construction; measurement uncertainty characterization; controlled evidence collection protocol.

### RQ2 — Human-centric AI-RAN orchestration

To what extent does twin-informed AI-RAN orchestration improve service continuity, worst-user QoE, fairness, reliability and resource efficiency across heterogeneous terrestrial and local-edge conditions when compared with static, network-only, service-priority and optimization-based baselines?

**Deliverables:** Five AI-RAN baselines; ablations; leave-one-zone/day/condition/workload holdouts; primary outcome analysis on `recovery_time_s`; practical significance thresholds.

### RQ3 — Resilient multi-access and NTN fallback

Under what outage, latency, capacity, mobility, blockage, energy and privacy conditions do terrestrial, local-edge, offline and NTN fallback policies improve continuity, and where do those policies fail or become counterproductive under measurement uncertainty?

**Deliverables:** Six resilience baselines; failure-boundary registry; source-validated NTN simulation aligned with external evidence (e.g., 3GPP TR 38.821); energy and privacy constraint analysis.

---

## 4. Related work positioning (concise)

| Theme | This work |
|-------|-----------|
| AI-RAN / ML for RRM | Twin-informed policies with explicit worst-user and fairness constraints; not black-box centralized training on raw UE data |
| Edge intelligence / FL | Privacy-preserving measurement at device; federated patterns as future extension—not claimed implemented |
| NTN / 6G multi-access | Failure-boundary focus; source-validated sim; no live commercial NTN control claim |
| Digital twins for wireless | Contract-first twin state from Edge-IO + network observations |
| QoE / human-centric networking | Workload intent and service classes drive orchestration—not throughput alone |

*Full bibliography seed: `../phd_application_readiness_package/11_bibliography_seed.md` — citations must be verified before submission.*

---

## 5. System architecture

```
Edge-IO (measurement, consent, privacy)
    → 7GC Digital Twin (context schemas, twin state)
        → SpectrumX AI-RAN (policies, baselines, ablations)
            → NTN Resilience Sim (multi-access fallback, failure boundaries)
                → Field-kit (contracts, validation, evidence reports)
```

**Gate 2 evidence:** Executable path with schema-validated artifacts (`GATE2_SYSTEM_PASS`). This certifies **engineering completion**, not scientific superiority or pilot completion.

**Repository roles** (Gate 1 locked):

| Repository | Role |
|------------|------|
| gunnchos-7gc-ai-ran-field-kit | Contracts, orchestration, evidence authority |
| edge-io-measurement-node | Privacy-preserving physical measurement |
| 7gc-digital-twin | Twin state construction |
| spectrumx-ai-ran-gary | AI-RAN orchestration |
| ntn-resilience-sim | Multi-access / NTN resilience |
| readygary-6g-beam-selection | Optional PHY support only |

---

## 6. Physical evidence design

### Pilot matrix

- **Design:** 3 zones × 2 network conditions × 3 days × 3 workloads = **54 sessions**
- **Session mode:** PILOT only (calibration/rehearsal excluded from eligible count)
- **Duration:** 300 seconds per session
- **Controls:** Consent before collection; privacy scan; assignment ID/hash; producer identity; sanitization

### Current status (honest)

| Item | Status |
|------|--------|
| Protocol frozen | AUTOMATION_READY — human zone/date approval pending |
| Five-minute rehearsal | PASS (infrastructure validation) |
| Calibration integrated runs | PASS → supports `GATE3_PARTIAL_EVIDENCE` only |
| Eligible pilot sessions | **0/54** |
| Zone identifiers | `PENDING_ZONE_*` |
| Collection dates | `PENDING_DATE_*` |

**Do not report `GATE_3_PASS` or `GATE_4_PASS`.**

---

## 7. Evaluation design (Gate 4)

Preregistered 2026-07-24. Primary outcome: **`recovery_time_s`**.

**AI-RAN baselines:** static_uniform, network_only, service_priority, optimization_based, twin_informed (proposed).

**Resilience baselines:** terrestrial_only, terrestrial_then_offline, always_ntn_on_terrestrial_failure, priority_class_fallback, service_aware_multi_access, oracle_hindsight (analysis only).

**Safeguards:** Grouped by day and zone; confidence intervals; effect sizes; practical significance thresholds; missing-data analysis; duplicate detection; split-leakage checks. Sessions are not treated as independent subjects.

**Status:** `GATE4_EVALUATION_READY` — automation and registries complete. Synthetic/calibration fixtures **never** produce Gate 4 PASS. Scientific evaluation **blocked** until eligible Gate 3 data frozen.

---

## 8. Three-paper doctoral roadmap

### Paper 1 — Privacy-Preserving Physical Measurement and Digital-Twin State (RQ1)

Scope: measurement node, consent, schemas, provenance, twin construction, uncertainty. Target venue class: IEEE IoT / measurement / privacy-aware systems workshop → journal extension.

### Paper 2 — Human-Centric Twin-Informed AI-RAN Orchestration (RQ2)

Scope: baselines, twin-informed policy, holdouts, ablations, worst-user QoE. Target: IEEE ICC/Globecom → TWC/TCOM track.

### Paper 3 — Service Continuity Through Local, Offline and NTN Resilience (RQ3)

Scope: fallback policies, failure boundaries, NTN simulation, energy/privacy constraints. Target: NTN/multi-access workshop → JSAC/survey companion.

*ReadyGary optional PHY results may appear as sensitivity analysis only.*

---

## 9. Research components (context, not products)

| Component | Research role | Completion honesty |
|-----------|---------------|-------------------|
| Device quartet | Four form-factor constraint classes | Concept/research-spec — not finished hardware products |
| WAIKE workloads | Realistic workload/context generator | Curriculum exists; dissertation is not education PhD |
| 7GC scenarios | Digital-twin scenario parameters | Gary primary pilot context; others simulation classes |
| gunnchOS middleware | Service-profile orchestration concept | Prototype-pending; evaluation via field-kit contracts |

---

## 10. Ethics and data governance

- No direct personal identifiers in canonical schemas  
- Consent-before-collection ordering enforced in validators  
- Gaza and other sensitive scenario classes: simulation-only unless explicit ethics/partner gates cleared (`../phd_application_readiness_package/09_ethics_data_permissions_note.md`)  
- AI tool use disclosure required at submission (`10_ai_use_statement.md`)

---

## 11. Timeline (4 years indicative)

| Year | Focus |
|------|-------|
| 1 | Gate 3 collection; Paper 1; evaluation freeze; Gate 4 on physical data |
| 2 | Papers 2–3 drafts; generalization adapters with verified licenses |
| 3 | Journal revisions; reproduction package (Gate 5); mock defense |
| 4 | Thesis integration; external review responses; archive (Gate 6) |

*Year 1 detail: `FIRST_YEAR_RESEARCH_PLAN.md`.*

---

## 12. Risk register

| Risk | Mitigation |
|------|------------|
| Pilot matrix incomplete | Preregistered missing-data analysis; partial evidence honestly reported |
| NTN claims overstated | Source-validated sim only; failure boundaries explicit |
| Privacy violation | Automated privacy scan; schema enforcement |
| Overclaiming | Claims verification matrix; red-line checklists |
| Supervisor mismatch | Multiple fit memos; no endorsement assumed |

---

## 13. Supervision and institutional fit

University of Oulu CWC / 6G Flagship alignment is documented in `supervisor-alignment/` (experimental test networks, distributed intelligence, NTN/IoT, signal processing). **No supervisor commitment is claimed.**

---

## 14. Evidence summary table

| Gate | Status | Claim allowed |
|------|--------|---------------|
| Gate 1 | PASS | Locked title, 3 RQs, 3 papers |
| Gate 2 | PASS | End-to-end executable pipeline |
| Gate 3 | HUMAN_ACTION_REQUIRED | Partial evidence only; 0/54 eligible |
| Gate 4 | AUTOMATION_READY | Evaluation-ready design; no physical PASS |
| Gate 5–6 | EXTERNAL_DEPENDENCY | Not started |

---

*Expand to institutional PDF template; verify bibliography before submission.*
