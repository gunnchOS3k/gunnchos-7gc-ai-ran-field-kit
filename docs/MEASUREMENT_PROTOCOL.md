# Measurement Protocol (Umbrella)

Combines field and simulation protocols without duplicating component repos.

## 1. Simulation path (default evidence)

See [methods/ai_ran_simulation_protocol.md](../methods/ai_ran_simulation_protocol.md) and component repo [spectrumx-ai-ran-gary](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary).

- Fixed seeds `{42…46}`
- Outputs: `results/benchmark/metrics.csv`, `results/ablation/ablation_table.csv`

## 2. Field path (exploratory)

See [methods/field_measurement_protocol.md](../methods/field_measurement_protocol.md) and [edge-io-measurement-node/docs/FIELD_TEST_PROTOCOL.md](https://github.com/gunnchOS3k/edge-io-measurement-node/blob/main/docs/FIELD_TEST_PROTOCOL.md).

- Opt-in only; waypoint labels
- No payload capture
- Repeated runs per waypoint (≥5)

## 3. Edge console path

See [methods/edge_console_protocol.md](../methods/edge_console_protocol.md).

- Offline-first logging (planned APK)
- CSV export matching telemetry schema

## 4. Integration (planned)

Sanitized aggregates from edge node → twin calibration labels → policy scenario profiles (Gary YAML).

## 5. Non-claims

This protocol does **not** define a citywide measurement campaign or operational AI-RAN closed loop.
