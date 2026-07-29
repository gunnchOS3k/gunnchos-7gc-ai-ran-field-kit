# Corrective-Depth Initial Audit (read-only baseline)

**Auditor:** Cursor corrective-depth pass  
**Timestamp (UTC):** 2026-07-29T20:22:00Z (session start)  
**Host:** Apple M2 — no NVIDIA GPU / CUDA / nvidia-smi / Docker for this pass  
**Rule:** statuses below are audit findings, not earned PASSes

## Repositories and exact commits (at audit start)

| repository | URL | branch (local) | default (origin) | HEAD | dirty | role |
|---|---|---|---|---|---|---|
| gunnchos-7gc-ai-ran-field-kit | https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit | cursor/corrective-depth-gates-4-6 | master | `d69a060024f573b5d23e0bd5066a55d5ed8ae8a2` | clean* | control plane |
| gunnchos-emergent-service-intent-protocols | https://github.com/gunnchOS3k/gunnchos-emergent-service-intent-protocols | cursor/corrective-depth-gates-4-6 | main | `0fee7ffe48a6e8ebe6cdc04176a2bad2dfe0336f` | clean | Oulu scientific |
| gunnchos-gpu-nr-baseband-platform | https://github.com/gunnchOS3k/gunnchos-gpu-nr-baseband-platform | cursor/corrective-depth-gates-4-6 | main | `51b910f90aae7be9c0044192eb2f13c91ef7bbfe` | clean | NVIDIA Aerial track |
| edge-io-measurement-node | https://github.com/gunnchOS3k/edge-io-measurement-node | cursor/corrective-depth-gates-4-6 | main | `b13156e351f14511786619d44ec5ee43e65e5140` | clean | Gate 6 sibling |
| 7gc-digital-twin | https://github.com/gunnchOS3k/7gc-digital-twin | cursor/corrective-depth-gates-4-6 | main | `62126f700db4ab429c28423e1212ba42b92c9d9b` | clean | Gate 6 sibling |
| ntn-resilience-sim | https://github.com/gunnchOS3k/ntn-resilience-sim | cursor/corrective-depth-gates-4-6 | main | `7ec94c219237b1d6767c234d9b40369a7dc377d6` | clean | Gate 6 sibling |
| spectrumx-ai-ran-gary | https://github.com/gunnchOS3k/spectrumx-ai-ran-gary | cursor/corrective-depth-gates-4-6 | main | `c7e2905f4bc4783b3bf2068a49bddd77cb19b941` | clean | Gate 6 sibling |
| readygary-6g-beam-selection | https://github.com/gunnchOS3k/readygary-6g-beam-selection | cursor/corrective-depth-gates-4-6 | main | `525405cb19d7987ad218272f5897d4917c10dd75` | clean | optional |
| gunnchos-hardware-industrial-design | https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design | cursor/corrective-depth-gates-4-6 | main | `ca5492c8e1c295975008b4dbf353b8a45a22069e` | clean | Gate 6 sibling |
| gunnchos-device-os | https://github.com/gunnchOS3k/gunnchos-device-os | cursor/corrective-depth-gates-4-6 | main | `26a9fd8b7cc2824a0b3d2d9769ce63710af1b42f` | clean | Gate 6 sibling |

\*Field-kit dirties appearance only when application-readiness regenerates local reports during audit reproduction.

Corrective branch for all repos: `cursor/corrective-depth-gates-4-6`.  
Oulu/NVIDIA: `main` tip was reset to the prior gates-4-6 tip for stable-branch topology; corrective branch forks from that tip.

## Current CI / local integrity failures (reproduced)

1. **Gate 2 / repository lock mismatch** — `integration/repo-lock.json` pinned 2026-07-24 SHAs; local siblings advanced (Gate 6 harness commits). `make verify-repo-lock` fails; integrated pipeline NON-REPRODUCIBLE.
2. **Application readiness** — FAIL via `verify_repo_lock` + `pytest_unit` (`test_valid_rehearsal_golden`, `test_repo_lock_matches_current_checkouts`) + `integrated_pipeline`.
3. **Valid rehearsal golden** — canonical hash still matches; `validate_assignment` fails solely because `expires_at=2026-07-24T23:11:04Z` < wall clock (wall-clock coupling in golden validation).

## Stale lock entries

Lock schema `1.1.0` components still point at:

- edge-io `3b42a7c…` (actual `b13156e…`)
- twin `fcc9b11…` (actual `62126f7…`)
- spectrumx `f7af6c7…` (actual `c7e2905…`)
- ntn `2403456…` (actual `7ec94c2…`)

Missing from Gate-2 lock (needed for Gates 4–6 portfolio lock completeness): Oulu, NVIDIA baseband, hardware-industrial-design, device-os, field-kit self.

`verify-repo-lock` correctly never rewrites; **`write-repo-lock` Make target is missing** (only verify exists).

## Missing Make targets (control plane)

Required corrective targets not yet present as named set:

- `corrective-audit`, `verify-inherited-ci`, `verify-repo-lock` (exists), `write-repo-lock` (missing)
- `gate4-oulu-scientific`, `gate4-nvidia-aerial-depth`, `gate5-publication-release`, `gate6-harness`, `all-corrective`

Legacy `gate4` / `gate6-dry-run` exist but award overly strong status labels.

## Status-label overclaims (prior pass)

Prior report used labels such as automated Gate 4/5 PASS based on smoke/scaffold. Corrective vocabulary until validators pass:

```text
CONTROL_PLANE_IMPLEMENTED_BUT_CI_RED
GATE4_OULU_FUNCTIONAL_SCAFFOLD_PASS
GATE4_OULU_SCIENTIFIC_EVIDENCE_PENDING
GATE4_NVIDIA_EDUCATIONAL_CPU_PASS
GATE4_NVIDIA_AERIAL_DEPTH_PENDING
GATE4_NVIDIA_GPU_PENDING
GATE5_DRAFT_PACKAGE_PASS
GATE5_PUBLICATION_RELEASE_PENDING
GATE6_PARTIAL_HARNESS_PASS
GATE6_PHYSICAL_EVIDENCE_PENDING
NVIDIA_TENURE_REQUIREMENT_UNSATISFIED
NVIDIA_CUSTOMER_TRIAL_REQUIREMENT_PENDING
NO_ACCEPTANCE_GUARANTEE
```

## Oulu scientific defects

- Messages stored but not reliably in receiver policy observations
- Service outcomes weakly coupled to control actions
- DIAL/TarMAC naming vs actual entropy/discrete PPO baselines
- QMIX/VDN incomplete (replay/targets/Double-Q suspected)
- Smoke ≠ 5-seed final matrix; manuscript mostly planned
- Missing causal / algorithm-fidelity completion validators

## NVIDIA technical defects

- Educational LDPC / DFT / hard LLR / AXPY still on acceptance-ish path
- Optimization “studies” are module benches, not controlled before/after
- No real `make gate6-dry-run` required by parent (parent falls back to ok:true)
- GPU numeric claims must remain `BLOCKED_HARDWARE` on this host

## Gate 5 publication defects

- `make paper` historically checks file presence more than result regeneration
- Application packs may contain absolute `/Users/...` paths and `commit: null`
- Author reproduction must not be labeled independent; DOI pending

## Gate 6 validation defects

- `scripts/run_gate6_dry_run.py` converts sibling Make failures into `{"ok": true}` + fallback note
- Parent `harness_ok` ignores sibling status
- Physical PASS must never derive from synthetic fixtures

## Application-pack defects

- Absolute local paths; null commits; private repos described without `REVIEWER_ACCESS_BLOCKED_USER_APPROVAL`

## Planned corrections (this pass)

1. Priority 0: lock write/verify separation; golden frozen-`now`; Gate 6 fail-closed; status dependency graph; completion validators; integrity negative tests
2. Priority 1: Oulu causal env + faithful MARL + pilot matrix + rewrite paper (parallel agent)
3. Priority 2: NVIDIA educational separation + NR path + CPU opt studies + gate6-dry-run (parallel agent)
4. Priority 3: real paper/artifact/reproduce-clean + portable packs
5. Rewrite lock only after corrective commits land; push draft PRs; no merge; publication `BLOCKED_USER_APPROVAL`

## Physical and external blockers

- 54-cell physical pilot; GPU/Nsight; NIC/PTP; SDR/RU; HW bring-up; OS physical boot; user study; independent reproduction; peer review; DOI; upstream acceptance; customer trials; ≥8y telecom tenure; Oulu/NVIDIA admission/hiring guarantees — all external/physical; never converted from dry-run
