# NET-SEC-6G-RC-001 (field-kit control plane)

**Product wording:** 5G-Advanced and NTN-capable, IMT-2030-aligned, software-defined, and engineered for migration to standardized 6G.

## Scope

Primary owner: `gunnchos-7gc-ai-ran-field-kit`  
Supporting (not disturbed this packet): device-os (Product-Use QEMU likely active), ntn-resilience-sim, spectrumx-ai-ran-gary, 6g-security lab, 7gc-digital-twin, edge-io.

## Machine-readable standards

- `standards/imt2030/{framework,technical_performance_requirements,evaluation_methods,test_environments,usage_scenarios}.json`
- `standards/3gpp/release_tracker.json`
- Official TPR numbers: `OFFICIAL_VALUE_PENDING` (Doc 5/116 TIES-restricted → SG5 Dec 2026)

## Digital runtimes (`net_sec_rc001/`)

5G-A RM520N-GL terrestrial · eSIM SGP.22 v2.7 interfaces · NTN LEO/MEO/GEO sim · AI-RAN safe recommend/rollback · service continuity · app QoS/QoE · hostile-network local · 6G migration delta · 7GC equitable scenarios.

## Run

```bash
python3 -m net_sec_rc001.evaluate
python3 -m standards.harnesses.imt2030_rel20_rel21_tracker
python3 -m standards.harnesses.imt2030_eval_harness
python3 -m pytest tests/test_net_sec_rc001.py tests/test_imt2030_rel20_rel21_tracker.py -q
```

## Forbidden

STANDARDIZED_6G · 6G_CERTIFIED · CARRIER_ACCEPTED · REAL_NTN_MODEM_VALIDATED · GATE_8_PASS · global IMT2030_PASS
