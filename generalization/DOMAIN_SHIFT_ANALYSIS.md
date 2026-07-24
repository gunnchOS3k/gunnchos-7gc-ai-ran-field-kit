# Domain Shift Analysis — Plan

**Status:** AUTOMATION_READY (plan only — **no GENERALIZATION_EVIDENCE_PASS**)  
**Date:** 2026-07-24

---

## Definition

**Domain shift** here means change in **scenario-class parameters** affecting connectivity stress: infrastructure density, NTN dependence, mobility, and degradation profiles—not geographic branding alone.

---

## Gary pilot (in-site primary)

| Scenario class | Role in thesis | Generalization |
|----------------|----------------|----------------|
| Gary underserved urban | Primary physical pilot (`PENDING_ZONE_*`) | **In-site only** until matrix complete |
| Ghana mobile-first | 7GC simulation parameters | Shift axis: bandwidth/sparsity |
| Guyana coastal/NTN | Simulation | Shift axis: weather + NTN share |
| Gaza offline-first | Ethics-gated simulation | Shift axis: outage duration |
| Geelong industrial | Simulation | Shift axis: reliability SLA |
| Germany cross-domain | Simulation | Shift axis: security boundary |
| Graham Land polar | Simulation | Shift axis: satellite-only |

Source: `../phd_application_readiness_package/06_7gc_digital_twin_scenario_requirements.md`

---

## Planned analysis (when adapters verified)

1. **Train/eval split:** Fit orchestration policies on Gary eligible cells only.  
2. **Simulation shift:** Apply 7GC scenario parameter cards without claiming measured evidence.  
3. **Open trace shift (future):** If M-Lab or other source reaches `VERIFIED_LICENSE`, replay trace-derived degradation profiles through twin pipeline.  
4. **Metrics:** Same primary `recovery_time_s` where defined; secondary QoE proxies labeled exploratory.  
5. **Report:** Effect direction and magnitude **per scenario class**; confidence intervals; failure regions.

---

## Claim boundaries

| Allowed | Not allowed |
|---------|-------------|
| "Policy ranking changed under scenario X parameters" | "Validated globally" |
| "Simulation shift suggests sensitivity to NTN share" | "Gary results generalize to Guyana" |
| "Open adapter refused unverified license" | "M-Lab confirms thesis" without verification |

---

## Dependencies

- Gate 3 eligible Gary data (currently 0/54)  
- `EVIDENCE_SOURCE_REGISTRY.yaml` entries with VERIFIED_LICENSE  
- `adapters/open_dataset_stub.py` or future verified adapters  

---

## Deliverable artifact (future)

`results/generalization/domain_shift_report.json` — **not created until execution authorized**

---

*Cross-reference: LIMITS_OF_GENERALIZATION.md*
