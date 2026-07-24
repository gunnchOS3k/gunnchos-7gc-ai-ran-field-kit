# Evaluation Preregistration

Locked at: `2026-07-24T01:38:45Z`
Primary outcome lock SHA-256: `43a441f312e69fcb64c5e094aa740874acfa19c63b86fce01b03e5ed1ceedc55`

## Primary claim

Under defined degraded-connectivity conditions, twin-informed service-aware orchestration reduces service outage or recovery time relative to static, network-only, and service-priority policies while respecting energy, fairness, privacy, and reliability constraints.

## Primary outcome

`recovery_time_s` — see PRIMARY_OUTCOME_LOCK.json for rationale.

## Baselines (AI-RAN)

1. static_uniform
2. network_only
3. service_priority
4. optimization_based
5. twin_informed (proposed)

## Resilience baselines

1. terrestrial_only
2. terrestrial_then_offline
3. always_ntn_on_terrestrial_failure
4. priority_class_fallback
5. service_aware_multi_access
6. oracle_hindsight_analysis_only

## Holdouts / ablations

See HOLDOUT_REGISTRY.yaml and ABLATION_REGISTRY.yaml (and existing evaluation/configs/).

## Statistical safeguards

Grouped by day and zone; CIs; effect sizes; practical significance thresholds; missing-data analysis; duplicate detection; split-leakage checks; do not treat 54 sessions as 54 independent people.

## Ordering

This preregistration is drafted before complete Gate 3 results inspection.
Status: AUTOMATION_READY pending Edmund freeze confirmation.
