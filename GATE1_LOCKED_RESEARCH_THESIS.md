# GATE 1 — LOCKED RESEARCH THESIS

**Status after merge of this change:** `GATE_1_PASS`  
**Version:** `1.0.0`  
**Date locked:** `2026-07-23`  
**Authority:** `gunnchos-7gc-ai-ran-field-kit`  
**Machine-readable companion:** `contracts/gate1_locked_thesis.v1.json`

---

## Exact title

Resilience-Aware, Human-Centric AI-RAN Orchestration for Service Continuity Across Terrestrial and Non-Terrestrial Networks

---

## Central hypothesis

A privacy-preserving orchestration architecture that combines physical device measurements, workload and service intent, digital-twin context, and terrestrial, local-edge and non-terrestrial network state can improve service continuity and worst-user quality of experience under sparse, degraded and disrupted connectivity when compared with static, network-only and service-priority baselines, while maintaining explicit fairness, energy, privacy and reliability constraints.

---

## Research questions (exactly three)

### RQ1 — Trustworthy context construction

How can privacy-preserving Edge-IO measurements, device state, workload intent and network observations be transformed into a reproducible digital-twin state that accurately represents user, service and connectivity conditions without collecting direct identifiers?

### RQ2 — Human-centric AI-RAN orchestration

To what extent does twin-informed AI-RAN orchestration improve service continuity, worst-user quality of experience, fairness, reliability and resource efficiency across heterogeneous terrestrial and local-edge conditions when compared with static, network-only, service-priority and optimization-based baselines?

### RQ3 — Resilient multi-access and NTN fallback

Under what outage, latency, capacity, mobility, blockage, energy and privacy conditions do terrestrial, local-edge, offline and NTN fallback policies improve continuity, and where do those policies fail or become counterproductive under measurement uncertainty?

---

## Three-paper doctoral roadmap

### Paper 1 — Privacy-Preserving Physical Measurement and Digital-Twin State

- **Primary repositories:** edge-io-measurement-node, 7gc-digital-twin, gunnchos-7gc-ai-ran-field-kit
- **Primary question:** RQ1
- **Scope:** physical measurement; consent and privacy; context schemas; provenance; twin-state construction; measurement uncertainty; controlled evidence collection.

### Paper 2 — Human-Centric Twin-Informed AI-RAN Orchestration

- **Primary repositories:** spectrumx-ai-ran-gary, 7gc-digital-twin, gunnchos-7gc-ai-ran-field-kit
- **Primary question:** RQ2
- **Scope:** static and adaptive policies; service classes; fairness; worst-user performance; optimization; baselines; held-out evaluation; ablations.

### Paper 3 — Service Continuity Through Local, Offline and NTN Resilience

- **Primary repositories:** ntn-resilience-sim, spectrumx-ai-ran-gary, gunnchos-7gc-ai-ran-field-kit
- **Primary question:** RQ3
- **Scope:** terrestrial degradation; local edge; delayed synchronization; offline operation; NTN fallback; recovery; failure boundaries; energy and privacy constraints; source-validated simulation.

---

## Repository-to-question matrix

| Repository | Required / optional | Primary RQ | Papers |
|---|---|---|---|
| gunnchos-7gc-ai-ran-field-kit | required | RQ1–RQ3 (contracts, orchestration, evidence) | 1, 2, 3 |
| edge-io-measurement-node | required | RQ1 | 1 |
| 7gc-digital-twin | required | RQ1, RQ2 | 1, 2 |
| spectrumx-ai-ran-gary | required | RQ2, RQ3 | 2, 3 |
| ntn-resilience-sim | required | RQ3 | 3 |
| readygary-6g-beam-selection | **optional** | supporting PHY / beam-state only | none (no fourth RQ/paper) |

ReadyGary is an optional supporting PHY experiment that may inform channel, blockage or beam-state assumptions. It is **not** a required flagship repository and does **not** create a fourth research question or paper.

---

## Included scope

- Privacy-preserving controlled-device measurement and consent lifecycle
- Canonical JSON Schema contracts and provenance across Edge-IO → 7GC → SpectrumX → NTN
- Twin-informed AI-RAN baselines, ablations, held-out evaluation design
- Source-validated NTN / multi-access resilience analysis
- Honest Gate status evaluation separating system completion from release/archive evidence

---

## Explicit non-goals

- Claiming deployment-scale 6G infrastructure
- Claiming live commercial NTN control
- Claiming regulatory or standards authority
- Collecting direct personal identifiers
- Claiming global generalization from the Gary pilot
- Claiming causal superiority from calibration data
- Treating ReadyGary as required for the full thesis
- Treating synthetic evidence as measured evidence

---

## Claim boundaries

| Claim class | Allowed when |
|---|---|
| System / engineering completion | Executable schemas, pipelines, and privacy-safe proofs pass |
| Partial physical evidence | Valid controlled-device sessions exist but matrix incomplete |
| Scientific evaluation pass | Full eligible evidence + baselines + held-out + uncertainty complete |
| Release / archive completion | Clean-checkout + non-author reproduction + immutable release + DOI/archive |

Calibration evidence supports infrastructure validation only. It must not be used to claim pilot completion or causal superiority.

---

## Change-control policy

1. The exact title, hypothesis, three RQs, and three-paper map are locked in this document and in `contracts/gate1_locked_thesis.v1.json`.
2. Any change requires a new Gate 1 document version, updated JSON companion, validator agreement, and an explicit PR reviewed by Edmund Gunn Jr.
3. Component repositories must not redefine the flagship thesis title or add a fourth RQ without updating this authority first.
4. Optional repositories may be added or removed without changing the three RQs, provided they remain optional and non-blocking.

---

## Gate 1 status rule

`GATE_1_PASS` only when:

- this document,
- `contracts/gate1_locked_thesis.v1.json`,
- the repository map, and
- `scripts/validate_gate1_thesis.py`

agree exactly on title, hypothesis, RQs, papers, and optional/required repository roles.
