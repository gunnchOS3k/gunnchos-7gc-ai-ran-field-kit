# Gates 4–6 Initial Audit

**Program:** Oulu GENOME + NVIDIA Aerial Evidence  
**Audit date (UTC):** 2026-07-29T18:57:23Z  
**Auditor:** Cursor agent (read-only inventory, then implementation)  
**Host:** Apple M2 MacBook (darwin 25.5.0)  
**Control repository:** `gunnchos-7gc-ai-ran-field-kit`  
**Spine path:** `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos`

## Host toolchain

| Item | Status |
|---|---|
| Python | 3.11.2 |
| Apple clang++ | 21.0.0 (clang-2100.1.1.101) |
| cmake | 4.4.1 (`/opt/homebrew/bin/cmake`) |
| ninja | 1.13.2 |
| Docker | **Unavailable** |
| CUDA / nvcc / nvidia-smi | **Unavailable** |
| GPU model | Apple M2 (Metal) — **not** NVIDIA → `GATE4_NVIDIA_GPU_PENDING` / `BLOCKED_HARDWARE` |
| PyTorch | 2.13.0, `torch.cuda.is_available() == False` |
| gh CLI | Authenticated as `gunnchOS3k` |
| Physical SDR / NIC PTP / RF lab | **Not inferred** — no connected lab instruments detected |

## Namespace collision note

This repository already contains a **different** Gates 1–7 scientific-evaluation program (`GATE_4_PASS` = authentic-data evaluation; `GATE_5_PASS` = independent reproduction; etc.).  
Gates 4–6 in **this** program are namespaced as `GATES_4_6_*` / `make gate4` / `requirements/gates_4_6/` and must **not** rewrite or weaken existing claim boundaries. Existing Gate 4 evaluation readiness remains `GATE4_EVALUATION_READY` / scientific `GATE_4_PASS` blocked pending authentic pilot data.

## Repository inventory

| repository | pre-audit branch | HEAD | dirty | current tests | role alignment | reusable code | planned modifications |
|---|---|---|---|---|---|---|---|
| `gunnchos-7gc-ai-ran-field-kit` | `cursor/non-physical-application-completion-20260724` | `eba17f843a50e7a884f450f2472330219e3b1c7b` | clean | pytest contracts, gate1–4 status, integrated pipeline | Control plane + 54-cell pilot | `verify_repo_lock.py`, pilot matrix, session validators, evidence taxonomy | Add `requirements/gates_4_6/`, schemas, orchestrators, Make targets; preserve existing gates |
| `edge-io-measurement-node` | `main` | `3b42a7c82a7a785cde85e0dbda9ed864f348d447` | clean | pytest telemetry/privacy/adapters | Gate 6 field measurement | Session schemas, Android client, consent | Gate 6 dry-run fixtures + validators; no overwrite of unrelated work |
| `7gc-digital-twin` | `main` | `fcc9b11df3be2205efc501e724745b6947563be7` | clean | site/scenario pytest | Twin scenarios for Oulu adapters | Site registry, RF geometry | Adapter contract docs only unless harness needs fixtures |
| `ntn-resilience-sim` | `main` | `2403456d03d5eba6e4f56c0fd9e18e141ed2761a` | clean | outage/metrics pytest | TN/NTN failover scenarios | Failure models | Soft adapter consumption from Oulu env |
| `spectrumx-ai-ran-gary` | detached HEAD | `f7af6c7f7541360e07402f6927794116a1684d32` | clean | airan/tool adapter tests | Policy context | Decision bundles | Branch from detached HEAD; soft adapter only |
| `readygary-6g-beam-selection` | `main` | `525405cb19d7987ad218272f5897d4917c10dd75` | clean | metrics/adapters | Stretch multimodal | Metrics | Minimal Gate 6 edge-benchmark hook if needed |
| `gunnchos-hardware-industrial-design` | `phd-application-readiness-docs` | `a0237e042cf47225de063b41db38e95022b431a3` | clean | mechanical/firmware tests | Gate 6 HW prototype packet | Production track schemas | Prototype evidence schema + dry-run |
| `gunnchos-device-os` | `phd-application-readiness-docs` | `bdb98d099f3c4a69280363de557bf8f46f4aca6f` | clean | launcher/image tests | Gate 6 OS boot packet | Device profiles | Boot/suspend/update dry-run harness |
| `gunnchos-emergent-service-intent-protocols` | **created empty** | (none) | n/a | none | **Gate 4A Oulu direct-fit** | n/a | Full research codebase |
| `gunnchos-gpu-nr-baseband-platform` | **created empty** | (none) | n/a | none | **Gate 4B NVIDIA direct-fit** | n/a | Full C++20/CUDA-capable baseband platform |

## Duplicate / conflicting artifacts

| Artifact | Conflict | Resolution |
|---|---|---|
| Existing `make gate4-evaluate` / `GATE_4_PASS` | Name overlap with new Oulu/NVIDIA Gate 4 | Keep existing targets; new program uses `make gate4`, `gate4-oulu`, `gate4-nvidia-*`, statuses `GATE4_OULU_*` / `GATE4_NVIDIA_*` |
| Existing Gate 5/6 human/external actions | Different meaning | Document in `NON_NEGOTIABLES_GATES_4_6.md`; do not auto-flip legacy statuses |
| Downloads duplicates (`gunnchos-7gc-research-product-scine`, zip copies) | Stale copies | Canonical spine is `gunnchos-7gc-research-product-spine/repos` — do not create alternate clones |

## Missing dependencies (pre-implementation)

- New repos empty — need full scaffolding
- `CROSS_REPO_VERSION_LOCK.json` for Gates 4–6 (distinct from `integration/repo-lock.json`)
- cmake/ninja present; Docker absent → container path documented as optional
- CUDA absent → GPU path harness-only

## Physical-hardware availability

Inferred **only** from host inspection:

- No NVIDIA GPU
- No CUDA driver stack
- No Docker
- No SDR/USRP enumeration performed successfully as attached lab gear
- 54-cell pilot matrix present; **eligible physical sessions remain 0/54** (unchanged)

## Exact planned modifications

1. Field-kit: Gates 4–6 control plane, schemas, scripts, registries, Make targets, application evidence pack builder  
2. Create and implement Oulu research repo end-to-end  
3. Create and implement NVIDIA baseband repo end-to-end (CPU measured; GPU pending)  
4. Edge-IO / hardware / device-OS: Gate 6 harness extensions + synthetic dry-runs  
5. Soft adapters only into twin/NTN/spectrumx  
6. Draft PRs on `cursor/gates-4-6-genome-aerial-evidence`; **no merge**

## Branch policy

Working branch on all touched repos: `cursor/gates-4-6-genome-aerial-evidence`  
Base commits recorded above prior to implementation commits.
