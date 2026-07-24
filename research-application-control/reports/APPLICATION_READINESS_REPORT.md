# Application Readiness Report

Generated: `2026-07-24T01:48:11Z`

## Overall automated pipeline: **PASS**

APPLICATION_COMPLETE is **false** (authentic gates incomplete).

## Automated passes

- PASS: `validate_master_status`
- PASS: `validate_preregistration`
- PASS: `validate_pilot_assignments`
- PASS: `validate_application_packet`
- PASS: `validate_gate1`
- PASS: `verify_repo_lock`
- PASS: `pytest_unit`
- PASS: `gate4_evaluation_ready`
- PASS: `integrated_pipeline`

## Automated failures

- None

## Human actions / external dependencies

- HUMAN_ACTION_REQUIRED: `GATE_3_physical_collection` — 0/54 eligible PILOT sessions
- EXTERNAL_DEPENDENCY: `non_author_reproduction` — Requires independent human
- EXTERNAL_DEPENDENCY: `faculty_supervision_commitment` — No fabricated endorsement
- EXTERNAL_DEPENDENCY: `doi_deposit` — DOI_PENDING

## Integrity

- Synthetic fixtures may be used for infrastructure tests only.
- No physical Gate 3 evidence fabricated.
- No faculty endorsement, DOI, or paper submission claimed.
- `datasets/controlled/raw-private/` remains gitignored.

