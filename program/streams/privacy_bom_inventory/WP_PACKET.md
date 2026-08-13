# STREAM packet — privacy + digital inventory

## Why now
Privacy export/delete were placeholders. SBOM generation was a stub. License
register entries are `REVIEW_REQUIRED`. EXTERNAL pentest remains uncommissioned.
This packet makes the digital controls and inventory *enforceable and honest*
without inventing legal rights or E7.

## Scope
- device-os privacy controller and runtime privacy service
- SBOM/HBOM/AI-BOM scanner with `UNKNOWN_RELEASE_BLOCKING`
- Beat Link / Archive / AI-model license tracking (machine)
- Pentest readiness package (scope, hashes, endpoints, RoE schema)
- Field-kit STREAM ledger + schema + claim boundary

## Out of scope
- Claiming E7 / EXTERNAL_PENTEST_COMPLETE
- Starting WP-006 as a cycle work packet or Cycle 3
- Legal counsel sign-off
- Inventing music, dataset, or model redistribution rights
- Cursor merge

## Change class
B (policy + inventory automation)

## Severity
S1 for unknown provenance at release; S2 for placeholder DSAR until this packet

## Verification class
V1 digital tests in owner repo + field-kit honesty tests

## Exit (digital)
- [x] implementation
- [x] implementer tests
- [ ] independent verification
- [ ] Edmund merge (Cursor never merges)
- [ ] HUMAN/EXTERNAL legal
- [ ] EXTERNAL pentest execution
