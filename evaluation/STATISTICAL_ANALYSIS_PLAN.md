# Statistical Analysis Plan (Amendment 001)

Frozen with primary outcome amendment at `2026-07-24T15:50:50Z` — eligible sessions **0/54**; no authentic aggregate inspection.

## Estimands

1. **Primary:** `total_service_outage_time_s` per session (seconds; lower better).
2. **Secondary:** `time_to_recovery_s` per outage event — completed events only for mean/median/max; right-censored events contribute to censoring rate, not to completed-recovery means.

## Grouping and dependence

- Group by day and zone; do not treat 54 sessions as 54 independent people.
- Repeated measures within day/zone require cluster-aware or mixed-model treatment.

## Uncertainty

- Confidence intervals and effect sizes on primary session totals.
- Report probe cadence and half-interval observation bounds.
- Missing-probe gaps flagged when inter-sample delta > 2.5× median cadence.

## Censoring

- Session-ending unavailable intervals are right-censored for `time_to_recovery_s`.
- Do not impute a recovery time for censored events.
- Preserve outage counts and total outage duration (primary) including censored spans.

## Practical significance

- Threshold: 5.0 s on `total_service_outage_time_s` (see PRACTICAL_SIGNIFICANCE_THRESHOLDS.yaml).

## Safeguards

- Duplicate detection; split-leakage checks; missing-data analysis; negative/neutral results preserved.
