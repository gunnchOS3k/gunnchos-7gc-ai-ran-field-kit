# NET-SEC-6G-RC-001 (field-kit control plane)

**Product wording:** Software-defined architecture engineered for 5G-Advanced and NTN-capable paths (NTN via simulation), IMT-2030-aligned, and engineered for migration to standardized 6G; Quectel RM520N-GL digital baseline is Rel-16 NSA+SA Sub-6 terrestrial only — not 5G-Advanced hardware and not NTN.

## Honesty notes (PR #78 remediation)

- `5GA_TERRESTRIAL_DIGITAL_RUNTIME` = **false** (Rel-16 RM520N digital ≠ 5GA).
- Supporting: `5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME` = true when Rel-16 surface passes.
- `HOSTILE_NETWORK_DIGITAL` requires local loopback socket/TLS/DNS/policy cases coupled to Rel-16 + continuity — not tautological boolean tables.

## Run

```bash
python3 -m net_sec_rc001.evaluate
python3 -m pytest tests/test_net_sec_rc001.py tests/test_imt2030_rel20_rel21_tracker.py -q
```
