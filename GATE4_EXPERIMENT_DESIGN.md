# Gate 4 Scientific Evaluation Design

Gate 4 evaluates AI-RAN and resilience decisions with held-out scenarios, explicit baselines, ablations, uncertainty, sensitivity analysis, failure-boundary analysis, and retained negative/neutral outcomes.

## Status semantics

- `FAIL`: required evaluation artifacts, split integrity, privacy/consent checks, or provenance checks failed.
- `GATE4_EVALUATION_READY`: infrastructure is complete and reproducible, but evidence is synthetic/calibration-only or otherwise not eligible for inference.
- `GATE4_PARTIAL_EVALUATION`: non-synthetic evaluation exists but does not meet all Gate 4 requirements.
- `GATE_4_PASS`: reserved for sufficiently powered, non-synthetic, leakage-free evaluation with complete artifacts.

Synthetic and calibration-only dry-runs are always labeled `infrastructure_validation_only` and `insufficient_sample_size_for_inference`. They must never produce `GATE_3_PASS` or `GATE_4_PASS`.

## Baselines

AI-RAN baselines: `static_uniform`, `network_only`, `service_priority`, `optimization_based`, `twin_informed`.

Resilience baselines: `terrestrial_only`, `terrestrial_then_offline`, `always_ntn_on_terrestrial_failure`, `priority_class_fallback`, `service_aware_multi_access`, `oracle_hindsight_analysis_only`.

The oracle baseline is analysis-only and never deployable.

## Splits

The split builder creates leave-one-day-out, leave-one-zone-out, leave-one-network-condition-out, leave-one-workload-profile-out, and stress-scenario holdout splits. It checks session-ID exclusivity, duplicate hashes, and minimum sample size.

## Ablations

Gate 4 ablates Edge-IO observations, digital-twin context, service-continuity objective, fairness constraint, energy constraint, local-edge availability, uncertainty inputs, external/source-validated context, NTN option, and a simulated privacy decision constraint. Actual privacy controls remain enabled.

## Uncertainty and sensitivity

Uncertainty reports record method, confidence level, resampling count, seed, sample count, assumptions, and limitations. Sensitivity and failure-boundary analyses cover latency, jitter, packet loss, capacity, energy, local-edge availability, outage/recovery timing, NTN latency/capacity/availability, handover delay, mobility, blockage, service class, fairness threshold, and continuity threshold.
