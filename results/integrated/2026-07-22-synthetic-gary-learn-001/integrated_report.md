# Gate 2 Integrated Report

## Evidence honesty

- Edge input evidence level: `synthetic`
- Twin evidence level: `synthetic`
- Do not interpret synthetic fixtures as physical-device measurements.

## Data path

1. Edge measurement batch → `01_edge_measurements.json`
2. 7GC normalization → `02_twin_state.json`
3. SpectrumX policies → `03_airan_*_decision.json`
4. NTN resilience decision → `04_resilience_decision.json`

## Validation

Schema validation was enforced at every repository boundary using the field-kit
canonical JSON Schema Draft 2020-12 contracts. Provenance hashes and run IDs are
checked across stages.

## Policy comparison

Deployed AI-RAN policy for NTN stage: `twin_informed`

Twin-informed predicted metrics:

```json
{
  "predicted_latency_ms": 65.80000069461123,
  "predicted_reliability": 0.9975999999852211,
  "predicted_packet_loss_pct": 0.2400000014778963,
  "energy_use_j": 38.29000058894165,
  "fairness": 0.9999999999999968,
  "service_continuity_utility": 0.8663158386012777,
  "capacity_utilization": 1.0
}
```

## Selected resilience mode

- Mode: `terrestrial`
- Trigger: `terrestrial_superior`
- Continuity score (computed): `0.8433333333333333`

## Assumptions and uncertainty

NTN non-measured parameters are labeled in `assumptions_used` inside
`04_resilience_decision.json` (`configured` / `synthetic` as applicable).

AI-RAN predicted metrics use an explicit analytical model documented in
`metric_model_assumptions`.

## Benchmark / ablation / sensitivity

Artifacts:

- `benchmark_results.csv` — executed policy runtime distributions
- `ablation_results.csv` — executed ablations under fixed seed
- `sensitivity_results.csv` — executed NTN parameter sweeps

## Remaining evidence limitations

Gate status: `AUTOMATED_PIPELINE_PASS`

Unmet criteria:

```json
[
  "external evidence missing: physical_device_measurement",
  "external evidence missing: real_consent_metadata",
  "external evidence missing: clean_checkout_reproduction",
  "external evidence missing: non_author_reproduction",
  "external evidence missing: immutable_candidate_release",
  "external evidence missing: doi_or_archived_dataset"
]
```

## Reproduction command

```bash
python scripts/run_integrated_pipeline.py \
  --edge-input <path-to-edge-batch.json> \
  --repos-root .. \
  --output-root results/integrated \
  --strict
```
