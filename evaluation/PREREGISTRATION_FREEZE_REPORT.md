# Preregistration Freeze Report (Amendment 001)

Amended at: `2026-07-24T15:50:50Z`  
Status: **INTERNALLY_VALID_AWAITING_EDMUND_APPROVAL**

## Change

- Primary: `total_service_outage_time_s`
- Secondary: `time_to_recovery_s` (right-censored at session end)
- Prior freeze preserved under `evaluation/amendments/amendment_001/`

## Evidence

- Calculator: `scripts/compute_recovery_time.py`
- Tests: `tests/evaluation/test_recovery_time_metric.py`
- Lock SHA-256: `d8a09e55f644edf72510f343448a352df3223cf537333391a597f06f58caf726`
- Eligible sessions at amendment: **0/54**
- Aggregate-result inspection: **false**

## Gate note

`EVALUATION_PREREGISTERED` remains evidence-backed as amended design freeze, with explicit human approval required before collection.
