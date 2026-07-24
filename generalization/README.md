# Generalization Evidence Framework

**Status:** BLOCKED — **GENERALIZATION_EVIDENCE_PASS not claimed**  
**Date:** 2026-07-24

---

## Purpose

Plan and implement **verified** external dataset adapters for domain and device shift analysis—without treating open data as licensed until proven.

---

## Current status

| Component | Status |
|-----------|--------|
| Evidence source registry | AUTOMATION_READY |
| Domain shift analysis (document) | AUTOMATION_READY — analytical plan only |
| Device shift analysis (document) | AUTOMATION_READY — analytical plan only |
| Limits document | AUTOMATION_READY |
| Base adapter interface | AUTOMATION_READY |
| Open dataset adapter stub | AUTOMATION_READY — refuses unverified licenses |
| Tests | AUTOMATION_READY |

**Execution blocked** until authentic sources with verified licenses are registered in `EVIDENCE_SOURCE_REGISTRY.yaml`.

---

## Gary pilot boundary

The Gary local pilot provides **one** geographic/infrastructure context. Generalization claims require:

1. Registered external sources with license verification  
2. Adapter output in approved schema only  
3. Separate analysis from Gate 3 eligible sessions  
4. No conflation with synthetic fixtures  

---

## Synthetic policy

Synthetic data **only** under:

- `tests/fixtures/synthetic/`  
- `examples/synthetic/`  

Never imported by generalization adapters as external evidence.

---

## Files

| File | Role |
|------|------|
| EVIDENCE_SOURCE_REGISTRY.yaml | Source metadata + license status |
| DOMAIN_SHIFT_ANALYSIS.md | Scenario/class shift plan |
| DEVICE_SHIFT_ANALYSIS.md | Form-factor shift plan |
| LIMITS_OF_GENERALIZATION.md | Claim boundaries |
| adapters/base.py | Interface |
| adapters/open_dataset_stub.py | License-gated stub |
| tests/test_adapter_interface.py | Contract tests |

---

## Gate

**GENERALIZATION_EVIDENCE_PASS:** BLOCKED — execute adapters only after verified sources available.

---

*Do not mark PASS in MASTER_STATUS until registry entries reach VERIFIED_LICENSE.*
