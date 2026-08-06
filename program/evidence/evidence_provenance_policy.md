# Evidence Provenance Policy

1. Every evidence record must include provenance (path, content hash, or git commit).
2. Physical measurements require linkage to `PHYSICAL_EVIDENCE_REGISTRY.json` / `physical_gate_registry.yaml`.
3. External acceptances require linkage to `external_gate_registry.yaml`.
4. Fabricated evidence is prohibited.
5. `GATE_0_PASS` requires Edmund approval evidence in `CHARTER_APPROVAL_RECORD.yaml`.
6. Simulation or unit-test evidence cannot satisfy hardware-measured or field-validated claims.
