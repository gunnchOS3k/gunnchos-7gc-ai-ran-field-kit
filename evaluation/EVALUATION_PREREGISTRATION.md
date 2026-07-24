# Evaluation Preregistration (Amendment 001)

**Status: INTERNALLY_VALID_AWAITING_EDMUND_APPROVAL**  
Amended at: `2026-07-24T15:50:50Z`  
Primary outcome lock SHA-256: `d8a09e55f644edf72510f343448a352df3223cf537333391a597f06f58caf726`  
Eligible pilot sessions: **0/54**  
Complete-pilot results inspected: **false**  
Prior freeze preserved: `evaluation/amendments/amendment_001/`

## Primary claim

Under defined degraded-connectivity conditions, twin-informed service-aware orchestration reduces total service outage time relative to static, network-only, and service-priority policies while respecting energy, fairness, privacy, and reliability constraints.

## Primary outcome

`total_service_outage_time_s` — total unavailable duration within the session.

## Secondary outcome

`time_to_recovery_s` — per-outage event recovery time with right-censoring at session end.

## Why amended

The prior `recovery_time_s` implementation summed unavailable intervals (total outage duration). Amendment 001 renames and locks that estimand as the primary outcome and separates event-level recovery with proper censoring.

## Baselines / holdouts / ablations / statistics

Unchanged registries: BASELINE_REGISTRY.yaml, ABLATION_REGISTRY.yaml, HOLDOUT_REGISTRY.yaml, STATISTICAL_ANALYSIS_PLAN.md.

## Approval gate

Physical collection must not begin until Edmund approves this amendment.
