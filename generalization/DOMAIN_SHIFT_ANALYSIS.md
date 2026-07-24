# Domain Shift Analysis — NordicDat Public Study

**Status:** **EXECUTED** (public dataset only — **no GENERALIZATION_EVIDENCE_PASS**)  
**Date:** 2026-07-24  
**Evidence label:** `public_dataset_not_physical_pilot` — separate from Gary physical pilot

---

## Definition

**Domain shift** here means change in **scenario-class parameters** affecting connectivity stress: access technology (LTE vs 5G), operator context, mobility/highway driving profiles, and degradation profiles—not geographic branding alone.

---

## Source executed

| Item | Detail |
|------|--------|
| Dataset | NordicDat (Zenodo 10964584) |
| License | CC BY 4.0 (VERIFIED_LICENSE) |
| Adapter | `generalization/adapters/nordicdat/adapter.py` |
| Config | `generalization/configs/nordicdat.yaml` |
| Output | `datasets/external/transformed/nordicdat/domain_shift_report.json` |

M-Lab NDT remains blocked (`blocked_pending_access`); NordicDat used as reproducible public alternative — see `PUBLIC_DATASET_STUDY.md`.

---

## Gary pilot (in-site primary — unchanged)

| Scenario class | Role in thesis | Generalization |
|----------------|----------------|----------------|
| Gary underserved urban | Primary physical pilot (`PENDING_ZONE_*`) | **In-site only** until matrix complete |
| Ghana mobile-first | 7GC simulation parameters | Shift axis: bandwidth/sparsity |
| Guyana coastal/NTN | Simulation | Shift axis: weather + NTN share |
| Gaza offline-first | Ethics-gated simulation | Shift axis: outage duration |
| Geelong industrial | Simulation | Shift axis: reliability SLA |
| Germany cross-domain | Simulation | Shift axis: security boundary |
| Graham Land polar | Simulation | Shift axis: satellite-only |

---

## Public dataset analysis performed

1. **Ingest:** Verified CC BY 4.0 license; downloaded checksummed CSV from Zenodo.  
2. **Normalize:** Map `delay` → `latency_ms`, throughput columns → kbps, `ran` → `access_technology`; strip geolocation fields.  
3. **Domain shift axis:** Compare LTE vs 5G latency and downlink throughput distributions.  
4. **Metrics:** Count, mean, median, p95 per technology group.  
5. **Label:** Results tagged `public_dataset_evidence_separate_from_physical_pilot`.

---

## Claim boundaries

| Allowed | Not allowed |
|---------|-------------|
| "Public NordicDat traces show LTE vs 5G QoS separation under border-highway context" | "Validated globally" |
| "Open adapter executed on verified CC BY 4.0 source" | "Gary results generalize to Finland/Sweden/Norway" |
| "Domain-shift exploratory evidence from one public source" | "GENERALIZATION_EVIDENCE_PASS" |

---

## Study status

| Record | Status |
|--------|--------|
| `public_dataset_source_1` | PASS |
| `remaining_authentic_sources` | ≥ 1 |
| `GENERALIZATION_EVIDENCE_PASS` | BLOCKED |

---

## Findings (public dataset only, 2026-07-24)

From `datasets/external/transformed/nordicdat/domain_shift_report.json` (91,455 normalized rows):

| Group | Latency mean (ms) | Latency p95 (ms) | Downlink mean (kbps) |
|-------|-------------------|------------------|----------------------|
| LTE | 148.1 | 421.0 | 4,122.9 |
| 5G (from 5G-NSA) | 96.0 | 328.0 | 10,718.2 |

Interpretation: exploratory domain-shift signal only (access-technology separation in Nordic border-highway context). **Not** a Gary pilot or global generalization claim.

---

## Dependencies still open

- Gate 3 eligible Gary data (currently 0/54 physical sessions)  
- Second authentic generalization source for B7 unblock  
- Pre-specified comparison to Gary twin-state schema once pilot data exists  

---

*Cross-reference: PUBLIC_DATASET_STUDY.md, LIMITS_OF_GENERALIZATION.md*
