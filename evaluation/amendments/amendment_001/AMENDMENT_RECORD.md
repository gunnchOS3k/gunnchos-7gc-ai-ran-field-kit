# Amendment 001 — Primary outcome clarification

| Field | Value |
|-------|-------|
| Amended at | 2026-07-24T16:00:00Z (approx) |
| Eligible pilot sessions at amendment | **0/54** |
| Authentic aggregate-result inspection | **false** |
| Reason | Prior primary `recovery_time_s` summed unavailable intervals across a session, which measures **total outage duration**, not a single recovery-time estimand. |
| Change | Adopt `total_service_outage_time_s` as primary; retain event-level `time_to_recovery_s` as secondary with right-censoring. |
| Status | Internally valid; **awaiting Edmund final approval** before physical collection |

Original locked files in this directory are preserved byte-for-byte from the prior freeze.
