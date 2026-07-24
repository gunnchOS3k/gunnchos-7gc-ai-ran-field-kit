# Public Dataset Generalization Study — NordicDat

**Date:** 2026-07-24  
**Status:** `public_dataset_source_1` = **PASS**  
**GENERALIZATION_EVIDENCE_PASS:** **BLOCKED** (not claimed)

---

## Dataset chosen

| Field | Value |
|-------|-------|
| Name | NordicDat (`nordicdat`) |
| Title | NordicDat: A Cross-Border Predictive QoS Dataset |
| Source | [Zenodo 10964584](https://zenodo.org/records/10964584) |
| DOI | [10.5281/zenodo.10964584](https://doi.org/10.5281/zenodo.10964584) |
| License | **Creative Commons Attribution 4.0 International (CC BY 4.0)** |
| Size | ~14.3 MB CSV (~90k rows) |
| Evidence class | `public_dataset_not_physical_pilot` |

---

## Why not M-Lab NDT (registered but blocked)

M-Lab NDT is CC0-licensed but **raw archival download requires** the M-Lab Acceptable Use Agreement plus GCS/BigQuery credentials (`mlab-ndt-cc0` remains `blocked_pending_access` in `datasets/external/registry/external_dataset_registry.json`). NordicDat provides a **direct HTTPS CSV download** with a published MD5 checksum and explicit CC BY 4.0 terms on Zenodo — suitable for reproducible, checksummable public generalization evidence without credential gates.

---

## Study status record

| Gate | Status |
|------|--------|
| `public_dataset_source_1` | **PASS** |
| `remaining_authentic_sources` | **≥ 1** (NTN TR 38.821 reference + pending second open/physical source) |
| `GENERALIZATION_EVIDENCE_PASS` | **BLOCKED** |

Public dataset evidence is **labeled separately** from Gary physical pilot data (`INTERNAL_CONSENT_GATED`).

---

## Commands

```bash
make generalization-download DATASET=nordicdat
make generalization-verify DATASET=nordicdat
make generalization-preprocess DATASET=nordicdat
make generalization-evaluate DATASET=nordicdat
```

Equivalent:

```bash
python3 scripts/run_generalization.py download --dataset nordicdat
python3 scripts/run_generalization.py verify --dataset nordicdat
python3 scripts/run_generalization.py preprocess --dataset nordicdat
python3 scripts/run_generalization.py evaluate --dataset nordicdat
```

---

## Artifacts

| Path | Role |
|------|------|
| `generalization/configs/nordicdat.yaml` | Source metadata, license, schema mapping |
| `generalization/adapters/nordicdat/adapter.py` | License-gated adapter |
| `generalization/manifests/nordicdat.json` | Download checksum manifest |
| `datasets/external/source/nordicdat/nordicdat.csv` | Raw public CSV (not Gate 3) |
| `datasets/external/transformed/nordicdat/normalized_records.json` | Preprocessed normalized records |
| `datasets/external/transformed/nordicdat/domain_shift_report.json` | LTE vs 5G domain-shift summary |
| `generalization/tests/test_nordicdat_adapter.py` | Adapter contract tests |

---

## Checksums

| File | MD5 (upstream) | SHA256 (local, post-download) |
|------|----------------|-------------------------------|
| `nordicdat.csv` | `3681daeaccfa78654858922c0df4a863` | `d1637c587ac01ce41ee24115eaa07758006bd513cf806a5daec31caf075c0249` |
| `normalized_records.json` | — | `943eb6d2d3b8260a01b8b58d7173d1fb4d51cabe8568159a9c07e93d7893d3a8` |

---

## Intended use

Compare public LTE vs 5G QoS distributions (latency, throughput, RSRP/SINR) as **domain-shift exploratory evidence** aligned with twin-state connectivity axes. Does **not** substitute for Gary controlled pilot sessions or claim global generalization.

---

## Citation (required under CC BY 4.0)

Miekkala, Topi, Pyykonen, Pasi, & Drainakis, Georgios (2024). NordicDat: A Cross-Border Predictive QoS Dataset [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10964584

---

*Do not mark GENERALIZATION_EVIDENCE_PASS until ≥2 authentic generalization sources are executed and reviewed.*
