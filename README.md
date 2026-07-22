# gunnchos 7GC Field Console: Phone-First AI-RAN Measurement Kit

**Umbrella research artifact** for an **IMT-2030-aligned / 6G-aligned** portfolio coupling AI-assisted O-RAN-style policy experiments with a **phone-first field console** for exploratory edge measurements.

This is a **research prototype**, not commercial 6G, carrier-grade AI-RAN, or citywide deployment.

---

## Component repositories

| Component | Repository | Role |
|-----------|------------|------|
| AI-RAN / spectrum engine | [spectrumx-ai-ran-gary](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary) | Synthetic policy benchmarks, optional SpectrumX path |
| Edge measurement node | [edge-io-measurement-node](https://github.com/gunnchOS3k/edge-io-measurement-node) | Opt-in telemetry schema + probes |
| Digital equity pilot (planned) | `gunnchos-digital-equity-wireless-pilot` | Community consent + operations |

---

## Conference readiness status

| Artifact | Path |
|----------|------|
| System overview | [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) |
| Measurement protocol | [docs/MEASUREMENT_PROTOCOL.md](docs/MEASUREMENT_PROTOCOL.md) |
| Source matrix (60-pack) | [docs/SOURCE_MATRIX.md](docs/SOURCE_MATRIX.md) |
| Publication plan | [docs/PUBLICATION_PLAN.md](docs/PUBLICATION_PLAN.md) |
| Privacy & ethics | [docs/PRIVACY_AND_ETHICS.md](docs/PRIVACY_AND_ETHICS.md) |
| Claims ↔ evidence | [docs/CLAIMS_TO_EVIDENCE.md](docs/CLAIMS_TO_EVIDENCE.md) |
| IEEE draft | [paper/ieee_conference_draft.md](paper/ieee_conference_draft.md) |

---

## Reproduce core results

```bash
# AI-RAN synthetic benchmark
git clone https://github.com/gunnchOS3k/spectrumx-ai-ran-gary.git
cd spectrumx-ai-ran-gary && pip install -r requirements.txt
make test && make benchmark && make ablation

# Edge telemetry schema + probes
git clone https://github.com/gunnchOS3k/edge-io-measurement-node.git
cd edge-io-measurement-node && pip install -r requirements.txt
make test
```

---

## What is real vs synthetic vs planned

| Status | Examples |
|--------|----------|
| **Real today** | Deterministic synthetic benchmarks; schema-validated telemetry examples; CI smoke tests |
| **Synthetic-only evidence** | AI-RAN ablation tables; emulator telemetry |
| **Planned** | Field campaigns; Zenodo DOI; near-RT RIC integration; Android APK |
| **Not claimed** | Deployable 6G; carrier AI-RAN; citywide impact; unauthorized RF transmission |

---

## Citation

See [CITATION.cff](CITATION.cff). Zenodo DOI: **planned** (see [docs/PUBLICATION_PLAN.md](docs/PUBLICATION_PLAN.md)).

---

## License

MIT — see [LICENSE](LICENSE).


---

## Gate 2 integrated system (contracts + orchestration)

This repository is the **canonical contract authority** for Gate 2.

```bash
pip install -r requirements.txt
make test
make contract-test
make integrated-pipeline EDGE_INPUT=fixtures/valid/edge_measurement_batch.valid.json
make reproduce EDGE_INPUT=fixtures/valid/edge_measurement_batch.valid.json
```

Evidence labels:
- `synthetic` — emulator/fixtures only
- `controlled_device_measurement` — physical device only (not present until captured)

Automated completion yields `AUTOMATED_PIPELINE_PASS`. Full `GATE_2_PASS` requires external evidence listed in `GATE2_EXTERNAL_EVIDENCE_CHECKLIST.md`.
Final merge approver: **Edmund Gunn Jr.**
