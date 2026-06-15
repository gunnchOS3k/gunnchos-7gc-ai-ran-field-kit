# Claims to Evidence (Umbrella)

Statuses: `proven` | `synthetic-only` | `planned` | `not claimed`

| Claim | Status | Evidence |
|-------|--------|----------|
| Umbrella docs link three research products | proven | This README + [docs/SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) |
| AI-RAN synthetic benchmark reproducible | synthetic-only | [spectrumx-ai-ran-gary](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary) `make benchmark` |
| Policy ablation (4 variants) | synthetic-only | `make ablation` → `results/ablation/ablation_table.csv` |
| Telemetry schema + probe modules | proven | [edge-io-measurement-node](https://github.com/gunnchOS3k/edge-io-measurement-node) `make test` |
| Sample telemetry JSON/CSV | proven | `examples/sample_telemetry.*` |
| IEEE conference draft exists | proven | [paper/ieee_conference_draft.md](../paper/ieee_conference_draft.md) |
| Field campaign represents Gary citywide | not claimed | — |
| Operational near-RT RIC xApp | not claimed | Export stubs only |
| Deployable 6G network | not claimed | — |
| Carrier-grade AI-RAN | not claimed | — |
| Zenodo DOI | planned | [docs/PUBLICATION_PLAN.md](PUBLICATION_PLAN.md) |
| Digital equity pilot operations | planned | Future `gunnchos-digital-equity-wireless-pilot` |
| Android APK field console | planned | [ANDROID_FIELD_CONSOLE_ROADMAP](https://github.com/gunnchOS3k/edge-io-measurement-node/blob/main/docs/ANDROID_FIELD_CONSOLE_ROADMAP.md) |

Component matrices:

- [spectrumx CLAIMS_TO_EVIDENCE_MATRIX](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/blob/main/quality/CLAIMS_TO_EVIDENCE_MATRIX.md)
- edge-io `quality/CLAIMS_TO_EVIDENCE_MATRIX.md` (if present)
