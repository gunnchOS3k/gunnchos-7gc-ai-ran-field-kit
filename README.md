# gunnchos 7GC Field Console: Phone-First AI-RAN Measurement Kit

**Umbrella research artifact** for an **IMT-2030-aligned / 6G-aligned** portfolio coupling AI-assisted O-RAN-style policy experiments with a **phone-first field console** for exploratory edge measurements.

This is a **research prototype**, not commercial 6G, carrier-grade AI-RAN, or citywide deployment.

---

## Portfolio position

This repo is the **umbrella** for the research spine:

```text
gunnchos-7gc-ai-ran-field-kit  ← you are here
  → spectrumx-ai-ran-gary
  → edge-io-measurement-node
  → 7gc-digital-twin
  → ntn-resilience-sim
  → readygary-6g-beam-selection
  → gunnchos-7gc-verticals-6g-use-case-lab
```

Public index: [gunnchos-research-portal](https://github.com/gunnchOS3k/gunnchos-research-portal)

---

## Component repositories

| Component | Repository | Role |
|-----------|------------|------|
| AI-RAN / spectrum engine | [spectrumx-ai-ran-gary](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary) | O-RAN-style / AI-RAN-inspired synthetic benchmarks |
| Edge measurement node | [edge-io-measurement-node](https://github.com/gunnchOS3k/edge-io-measurement-node) | Opt-in telemetry schema + probes |
| Digital twin | [7gc-digital-twin](https://github.com/gunnchOS3k/7gc-digital-twin) | Twin research prototype |
| NTN resilience | [ntn-resilience-sim](https://github.com/gunnchOS3k/ntn-resilience-sim) | Simulation only |
| Beam selection | [readygary-6g-beam-selection](https://github.com/gunnchOS3k/readygary-6g-beam-selection) | 6G-aligned algorithms |
| Verticals lab | [gunnchos-7gc-verticals-6g-use-case-lab](https://github.com/gunnchOS3k/gunnchos-7gc-verticals-6g-use-case-lab) | Use-case exploration |
| Device console | [gunnchos-device-os](https://github.com/gunnchOS3k/gunnchos-device-os) | Phone-first field console software |
| Education | [waike-research-ops](https://github.com/gunnchOS3k/waike-research-ops) → [gunnchAI3k](https://github.com/gunnchOS3k/gunnchAI3k) | Learner pathways + tutor |

---

## Mission & evidence docs

| Doc | Path |
|-----|------|
| Mission alignment | [MISSION_ALIGNMENT.md](MISSION_ALIGNMENT.md) |
| Claims ↔ evidence | [CLAIMS_TO_EVIDENCE.md](CLAIMS_TO_EVIDENCE.md) |
| Reproducibility | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Accessibility / low cost | [ACCESSIBILITY_AND_LOW_COST.md](ACCESSIBILITY_AND_LOW_COST.md) |
| IEEE readiness audit | [quality/IEEE_ARTIFACT_READINESS_AUDIT.md](quality/IEEE_ARTIFACT_READINESS_AUDIT.md) |
| IEEE draft | [paper/ieee_conference_draft.md](paper/ieee_conference_draft.md) |

---

## Conference readiness status

| Artifact | Path |
|----------|------|
| System overview | [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) |
| Measurement protocol | [docs/MEASUREMENT_PROTOCOL.md](docs/MEASUREMENT_PROTOCOL.md) |
| Eval protocol | [docs/EVAL_PROTOCOL.md](docs/EVAL_PROTOCOL.md) |
| Source matrix | [docs/SOURCE_MATRIX.md](docs/SOURCE_MATRIX.md) |
| Publication plan | [docs/PUBLICATION_PLAN.md](docs/PUBLICATION_PLAN.md) |
| Privacy & ethics | [docs/PRIVACY_AND_ETHICS.md](docs/PRIVACY_AND_ETHICS.md) |
| Detailed claims matrix | [docs/CLAIMS_TO_EVIDENCE.md](docs/CLAIMS_TO_EVIDENCE.md) |

---

## Reproduce core results

```bash
python3 scripts/check_required_files.py

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
| **Real today** | Deterministic synthetic benchmarks; schema-validated telemetry examples; CI smoke tests; umbrella documentation |
| **Synthetic-only** | AI-RAN ablation tables; emulator telemetry |
| **Planned** | Field campaigns; Zenodo DOI; near-RT RIC integration; Android APK |
| **Not claimed** | Deployable 6G; carrier AI-RAN; citywide impact; unauthorized RF transmission |

---

## Citation

See [CITATION.cff](CITATION.cff). Zenodo DOI: **planned** (see [docs/PUBLICATION_PLAN.md](docs/PUBLICATION_PLAN.md)).

## License

MIT — see [LICENSE](LICENSE).
