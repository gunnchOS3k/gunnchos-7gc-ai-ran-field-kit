# Evaluation Preregistration

**Status: PASS (frozen)**  
Frozen at: `2026-07-24T15:04:05Z`  
Primary outcome lock SHA-256: `bcf035b67e88f4fcc25284b5dab3d53101ae7a38e65e00703f8ff7e37c0290f9`  
Eligible pilot sessions at freeze: **0/54**  
Complete-pilot results inspected: **false**

## Primary claim

Under defined degraded-connectivity conditions, twin-informed service-aware orchestration reduces service outage or recovery time relative to static, network-only, and service-priority policies while respecting energy, fairness, privacy, and reliability constraints.

## Primary outcome

`recovery_time_s` — physically derived from `edge_measurement_batch` via `scripts/compute_recovery_time.py`.

### Operational definition

| Element | Definition |
|---------|------------|
| Units | seconds |
| Lower is better | yes |
| Start event | first unavailable sample (`latency_ms` null OR `probe_timeout` OR `service_available==false`) |
| Recovery event | first subsequent available sample |
| Timeout / censoring | unrecovered outages censored at last sample timestamp |
| Failure | `null` only if empty measurements or invalid timestamps |
| Unavailable data | nulls preserved; probe_timeout marks unavailable |
| Practical significance | 5.0 seconds (see PRACTICAL_SIGNIFICANCE_THRESHOLDS.yaml) |
| Not primary | `expected_recovery_time_s` model estimate |

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

See HOLDOUT_REGISTRY.yaml and ABLATION_REGISTRY.yaml.

## Statistical safeguards

Grouped by day and zone; CIs; effect sizes; practical significance; missing-data analysis; duplicate detection; split-leakage checks; do not treat 54 sessions as 54 independent people.

## Ordering evidence

This freeze occurs with Gate 3 at 0/54 eligible sessions and before any authentic full-pilot aggregate inspection.
