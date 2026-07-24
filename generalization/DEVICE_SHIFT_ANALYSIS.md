# Device Shift Analysis — Plan

**Status:** AUTOMATION_READY (plan only — **no GENERALIZATION_EVIDENCE_PASS**)  
**Date:** 2026-07-24

---

## Definition

**Device shift** means change in **resource constraint class** (compute, memory, energy, sensing modality)—not claiming multiple finished hardware product lines.

---

## Device quartet (research form factors)

| Form factor | Constraint focus | Workload proxy |
|-------------|------------------|----------------|
| Student 14.5" desk | Sustained session, moderate compute | Learning/work |
| Handheld hybrid | Mobility, bursty, docked expansion | Mobile demo |
| DS-XL coder | Heavy local compute, peer sync | Creation/deploy |
| Edge IO wearables | Ultra-low latency sensing | Kinesthetic/sensing |

Source: `../phd_application_readiness_package/04_device_quartet_research_requirements.md`

**Honest status:** Concept/research-spec — not finished product portfolio.

---

## Current physical evidence

Primary collection device: Pixel-class rehearsal path documented in Gate 3 reports. **Eligible pilot 0/54.** Other form factors evaluated via **parameter profiles** until hardware available.

---

## Planned analysis

1. **Profile replay:** Run identical network traces under four device profile YAML constraints.  
2. **Energy sensitivity:** Vary Edge-IO energy budget; document recovery_time_s vs policy changes.  
3. **Sensing modality (wearable):** Latency-bound workloads — separate QoE proxy.  
4. **Holdout:** Leave-one-form-factor-out if multiple physical devices later collected.  
5. **Adapter path:** Open device trace datasets only through verified-license adapters.

---

## Shift hypotheses (to test — not pre-claimed)

- Twin-informed gains **shrink** under tight energy budgets.  
- NTN fallback **hurts** wearable latency-bound workloads disproportionately.  
- optimization_based may **overfit** desk-class compute availability.

---

## Claim boundaries

| Allowed | Not allowed |
|---------|-------------|
| "Rankings shifted under wearable energy cap in simulation" | "Quartet products validated" |
| "Single-device pilot; profiles for other classes" | "Four devices measured in field" |

---

## Dependencies

- Device profile YAMLs in component repos  
- Optional additional hardware — not required pre-application  
- Verified external traces if used  

---

## Deliverable artifact (future)

`results/generalization/device_shift_report.json` — **not created until execution**

---

*Cross-reference: DEVICE_SHIFT_ANALYSIS.md, LIMITS_OF_GENERALIZATION.md*
