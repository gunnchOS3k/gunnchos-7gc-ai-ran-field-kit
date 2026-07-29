# Gates 4–6 Final Handoff (Draft — updated after orchestrator runs)

**Audience:** Edmund Gunn Jr. (sole merge approver)  
**Branch:** `cursor/gates-4-6-genome-aerial-evidence`

## What Cursor completed (automatable)

- Control-plane schemas, registries, Make targets, orchestrators
- Oulu research repository scaffold + tests/experiments (see repo PR)
- NVIDIA baseband C++20 portable path + CUDA conditional sources (see repo PR)
- Gate 6 harnesses and synthetic dry-runs
- Application evidence packs

## What remains physical / external

See `PHYSICAL_EVIDENCE_REGISTRY.json` and `EXTERNAL_GATE_REGISTRY.json`.

Ordered physical packets for Edmund:

1. **Field pilot (54-cell)** — Edge-IO + field-kit operators guide; evidence → `physical_evidence/`
2. **GPU lab** — Linux host + NVIDIA GPU + Nsight; baseband `docs/lab/`
3. **NIC/PTP** — Mellanox/NVIDIA NIC if available
4. **SDR/RU cabled** — authorized RF only
5. **Hardware prototype photos/bring-up** — hardware repo packet
6. **OS physical boot** — device-os signed image on real device
7. **User study** — ethics oversight; no IRB claim until approved
8. **Customer/partner trial** — external only

## External career gates (cannot be coded)

- 8+ years industry experience for NVIDIA role
- Real telecom customer/partner collaboration evidence

## Merge policy

Draft PRs only. Edmund reviews and merges.
