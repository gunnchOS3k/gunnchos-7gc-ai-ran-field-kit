# Ablation Conformance Report

**Generated:** 2026-07-24T15:05:00Z  
**Registry:** `evaluation/ABLATION_REGISTRY.yaml`, `evaluation/configs/ablations.yaml`  
**Run class:** Synthetic dry-run only (`make evaluate-ablations` without `DATASET=`)  
**Scientific Gate 4:** **BLOCKED**

---

## Purpose

Confirm ablation evaluation infrastructure matches preregistered ablation registry in dry-run mode, without interpreting fixture outputs as scientific results.

---

## Command

```bash
make evaluate-ablations
# Without DATASET= → BLOCKED:scientific_eval_pending_authentic_dataset
# → make gate4-evaluation-ready
```

**Observed (2026-07-24):** Dry-run artifacts at `results/gate4/gate4-run-20260724T150502Z/raw_results/ablation_results.csv`.

---

## Registry vs dry-run

| Ablation family (registry) | Dry-run column present | Scientific ablation |
|----------------------------|------------------------|---------------------|
| Twin-informed vs static | Structural | NO — fixture N=6 |
| Service-priority vs network-only | Structural | NO |
| Resilience path toggles | Structural | NO |
| Oracle hindsight (analysis-only) | Labeled non-deployable | NO |

Dry-run status explicitly lists oracle hindsight as **analysis-only and never deployable**.

---

## Integrated pipeline cross-check

Synthetic integrated run (`fixtures/valid/edge_measurement_batch.valid.json`) also produces `ablation_results.csv` under `results/integrated/` — same infrastructure class, not Gate 4 scientific pass.

---

## Verdict

| Dimension | Status |
|-----------|--------|
| Ablation registry ↔ script wiring | PASS (infrastructure) |
| Ablation on frozen Gate 3 data | BLOCKED |
| Claimed method superiority from ablations | **NOT AUTHORIZED** |

---

## Next action

`make evaluate-ablations DATASET=path/to/dataset_manifest.json` after Gate 3 eligible set is frozen and preregistration freeze is human-confirmed.
