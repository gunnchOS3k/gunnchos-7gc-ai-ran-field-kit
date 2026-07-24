# Holdout Conformance Report

**Generated:** 2026-07-24T15:05:00Z  
**Registry:** `evaluation/HOLDOUT_REGISTRY.yaml`, `evaluation/configs/held_out_scenarios.yaml`  
**Run class:** Synthetic dry-run only (`make evaluate-holdouts` without `DATASET=`)  
**Scientific Gate 4:** **BLOCKED**

---

## Purpose

Verify that holdout split machinery conforms to preregistered registries when invoked in infrastructure mode, without treating dry-run splits as scientific evidence.

---

## Command

```bash
make evaluate-holdouts
# Without DATASET= → BLOCKED:scientific_eval_pending_authentic_dataset
# → make gate4-evaluation-ready
```

**Observed (2026-07-24):** Dry-run completed; artifacts under `results/gate4/gate4-run-20260724T150502Z/splits/`.

---

## Split artifacts (dry-run)

| Artifact | Path | Notes |
|----------|------|-------|
| Split summary | `splits/split_summary.json` | Infrastructure validation |
| Leave-one network condition | `splits/leave_one_network_condition_out.json` | Registry-aligned structure |
| Leave-one workload profile | `splits/leave_one_workload_profile_out.json` | Registry-aligned structure |
| Stress scenario holdout | `splits/stress_scenario_holdout.json` | Registry-aligned structure |

Splits are generated from **synthetic fixture sample count (6)**, not from 54 eligible physical sessions.

---

## Registry conformance (structural)

| Registry entry | Present in dry-run splits | Scientific holdout valid |
|----------------|---------------------------|--------------------------|
| Network-condition LOO | Yes (schema) | NO — insufficient N |
| Workload-profile LOO | Yes (schema) | NO — insufficient N |
| Stress scenario holdout | Yes (schema) | NO — fixture data |

---

## Leakage posture

Dry-run splits operate on labeled synthetic sessions only. No authentic pilot assignment hashes are in scope. Full leakage audit deferred to `evaluation/LEAKAGE_AND_DUPLICATE_REPORT.md` and future runs with `DATASET=`.

---

## Verdict

| Dimension | Status |
|-----------|--------|
| Holdout script + registry alignment (infrastructure) | PASS |
| Holdout splits on frozen Gate 3 eligible data | BLOCKED (0/54) |
| `GATE_4_PASS` from holdout evaluation | **NOT CLAIMED** |

---

## Next action

After Gate 3 freeze: `make evaluate-holdouts DATASET=path/to/dataset_manifest.json` and re-run this conformance report against authentic splits.
