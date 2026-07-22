# Gate 2 Workspace Audit

Audit date: 2026-07-22

All six repositories were located as siblings under `/agent/repos`.

| Repository | Path | Remote | Base branch | Base commit | Dirty at audit | Python | Package manager | CLI | Makefile |
|---|---|---|---|---|---|---|---|---|---|
| edge-io-measurement-node | /agent/repos/edge-io-measurement-node | https://github.com/gunnchos3k/edge-io-measurement-node | main | 4c5679440449867c09529c1f028ea23533286629 | clean | 3.11+ / 3.12 runtime | pip + requirements.txt | `python -m edge_io_node` | yes |
| 7gc-digital-twin | /agent/repos/7gc-digital-twin | https://github.com/gunnchos3k/7gc-digital-twin | main | 5728fbce0397aef3b1e4d4798a549b7db39e19dc | clean | 3.11+ | pip + requirements.txt | `python -m seven_gc_twin` | yes |
| spectrumx-ai-ran-gary | /agent/repos/spectrumx-ai-ran-gary | https://github.com/gunnchos3k/spectrumx-ai-ran-gary | main | c0746ed855fafef971c3c7c5899f0aa482b88ea0 | clean | >=3.10 | pip + pyproject.toml | `python -m airan_research` (Gate 2) | yes |
| ntn-resilience-sim | /agent/repos/ntn-resilience-sim | https://github.com/gunnchos3k/ntn-resilience-sim | main | 9e0d308c7b01f6d7cd6292179793e857ab5080f9 | clean | 3.11+ | pip + requirements.txt | `python -m ntn_resilience` | yes |
| readygary-6g-beam-selection | /agent/repos/readygary-6g-beam-selection | https://github.com/gunnchos3k/readygary-6g-beam-selection | main | a13d1571f44c33c2a6538577113bee9a8cab2e3c | clean | 3.11+ | pip + requirements.txt | scripts under `scripts/` | yes |
| gunnchos-7gc-ai-ran-field-kit | /agent/repos/gunnchos-7gc-ai-ran-field-kit | https://github.com/gunnchos3k/gunnchos-7gc-ai-ran-field-kit | master | 760062c84fa6bd760208c8f287fe58adc61e13a6 | clean | 3.12 runtime | pip + requirements.txt (added) | scripts/ | added |

## Missing repositories

None. All six Gate 2 repositories are present.

## Integration risks recorded at audit

- Field-kit was documentation-only (no contracts/code).
- Component integration modules returned `smoke_contract` stubs.
- No shared schema-validated Edge→7GC→SpectrumX→NTN path existed.
- No physical-device measurement JSON was present.
- ReadyGary is optional and not required to block Gate 2 automation.

## Working branches

Feature branch for this effort: `cursor/gate2-integrated-system-3ec5` in each repository.
Final merge approver: Edmund Gunn Jr.
