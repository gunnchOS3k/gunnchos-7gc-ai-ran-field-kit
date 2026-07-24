# Pre-Collection Freeze Report

Generated: 2026-07-24

## Status

`PROVENANCE_AND_PROTOCOL_FROZEN` = **HUMAN_ACTION_REQUIRED**

## Automated acceptance (run locally)

| Check | Expected |
|-------|----------|
| `make verify-repo-lock` | PASS against locked SHAs |
| `python -m pytest -q` | PASS |
| `make integrated-pipeline` | PASS on fixtures |
| `make gate4-evaluation-ready` | PASS dry-run |
| `make pilot-validate-assignments` | PASS structure (54 cells); dates still PENDING |

## User-controlled protocol decisions still open

1. Exact Day 1–3 calendar dates (`PENDING_USER_DATE_*`)
2. Zone location categories for zone_a/b/c
3. Network degradation parameters + dry-run attestation
4. Signed `pilot/PILOT_DESIGN_APPROVAL.md`

## Explicit non-claims

- No physical Gate 3 sessions counted (0/54)
- Calibration/rehearsal do not count
- Freeze is **not** PASS until the open decisions above are resolved and automated checks re-verified
