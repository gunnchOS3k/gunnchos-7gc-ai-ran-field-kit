# GATE3 Evidence Report

Status: **GATE3_COLLECTION_READY**

## Required vs observed

```json
{
  "required": {
    "locations": 3,
    "network_conditions": 2,
    "distinct_days": 3,
    "workload_profiles": {
      "learn": 18,
      "create": 18,
      "sense": 18
    },
    "cells": 54,
    "planned_duration_seconds": 300
  },
  "observed": {
    "locations": 0,
    "network_conditions": 0,
    "distinct_days": 0,
    "eligible_sessions": 0,
    "physical_sessions": 0,
    "filled_cells": 0,
    "missing_cells": 54
  }
}
```

## Missing requirements

```json
[
  "minimum_distinct_day_coverage",
  "minimum_location_coverage",
  "minimum_network_condition_coverage",
  "minimum_repetitions",
  "no_physical_sessions_collected"
]
```

## Evidence honesty

- Physical sessions counted only when `evidence_level=controlled_device_measurement` and collector is not the emulator.
- Synthetic fixtures do not satisfy Gate 3.
- Label: descriptive pilot evidence (not publication-grade causal evaluation).

## External / source-validated evidence

`complete`

## Limitations

```json
[
  "Synthetic fixtures never satisfy Gate 3.",
  "M-Lab open-data download remains blocked pending AUA/GCS access.",
  "Physical pilot not executed in this automation environment."
]
```
