# GATE 1 Failure Reproduction

Generated: 2026-08-07T20:52:15Z

1. Remove or break a sibling game repo path and re-run `python -m gate1.orchestrator.cli run`.
2. Expect nonzero exit and `GATE_1_SOFTWARE_FAIL`.
3. Tamper a pending JSON `artifact_sha256` and run `validate-evidence` — expect rejection.
4. Attempt claim_level=PHYSICAL_BOOT with evidence_class=software — expect CLAIM_UPGRADE_REFUSED.
5. Call `accept-bundle` without Edmund decision record — expect refusal.
