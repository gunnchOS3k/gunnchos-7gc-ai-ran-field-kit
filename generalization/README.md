# Generalization Evidence Framework

**Status:** PARTIAL — `public_dataset_source_1` PASS; **GENERALIZATION_EVIDENCE_PASS not claimed**  
**Date:** 2026-07-24

---

## Purpose

Plan and implement **verified** external dataset adapters for domain and device shift analysis—without treating open data as licensed until proven.

---

## Current status

| Component | Status |
|-----------|--------|
| Evidence source registry | AUTOMATION_READY — NordicDat VERIFIED_LICENSE |
| Public dataset study (NordicDat) | **PASS** — `public_dataset_source_1` |
| Domain shift analysis (document) | **EXECUTED** (public dataset subset) |
| Device shift analysis (document) | AUTOMATION_READY — analytical plan only |
| Limits document | AUTOMATION_READY |
| Base adapter interface | AUTOMATION_READY |
| NordicDat adapter | AUTOMATION_READY — license-gated ingest |
| Open dataset adapter stub | AUTOMATION_READY — refuses unverified licenses |
| Tests | AUTOMATION_READY |

**Execution:** One authentic public dataset integrated. Physical pilot and full gate remain blocked.

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
| PUBLIC_DATASET_STUDY.md | NordicDat public generalization study |
| configs/nordicdat.yaml | Dataset config + schema mapping |
| adapters/nordicdat/adapter.py | NordicDat adapter |
| manifests/nordicdat.json | Download checksum manifest |
| DOMAIN_SHIFT_ANALYSIS.md | Scenario/class shift plan + public execution |
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
