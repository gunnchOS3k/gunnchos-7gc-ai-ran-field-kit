# Cross-Repo Implementation Plan — Gates 4–6

## Phase 0 — Audit (this document + `GATES_4_6_INITIAL_AUDIT.md`)

Complete before code mutation beyond branch creation.

## Phase 1 — Control plane (`gunnchos-7gc-ai-ran-field-kit`)

- Schemas for physical evidence, benchmark results, reproduction reports, lab instruments, user-study sessions  
- Orchestrators: `run_gate4.py`, `run_gate5.py`, `run_gate6_dry_run.py`, validators, application pack builder  
- `CROSS_REPO_VERSION_LOCK.json` pinned to commits; fail on mismatch  
- Registries for physical + external gates  
- Make targets listed in acceptance commands  

## Phase 2 — Gate 4A Oulu repo

Build `gunnchos-emergent-service-intent-protocols` as standalone research code with soft sibling adapters.

## Phase 3 — Gate 4B NVIDIA repo

Build `gunnchos-gpu-nr-baseband-platform` C++20 CPU path; CUDA conditional; GPU results blocked on this host.

## Phase 4 — Gate 5

Papers, ablations from real CPU runs, artifact packages, RC tags only after tests pass, DOI/reproduction pending.

## Phase 5 — Gate 6 harnesses

Field-kit 54-cell preservation, Edge-IO session dry-runs, HW/OS packets, user-study ethics packet (no IRB claim), lab protocols in baseband repo.

## Phase 6 — Validation + draft PRs

Run `make all-automatable`, fix failures, push branches, open **draft** PRs, do not merge.

## Dependency graph

```text
field-kit (control)
 ├── emergent-service-intent-protocols  (Gate 4A/5 Oulu)
 ├── gpu-nr-baseband-platform           (Gate 4B/5/6 NVIDIA)
 ├── edge-io-measurement-node           (Gate 6 field)
 ├── 7gc-digital-twin                   (soft adapter)
 ├── ntn-resilience-sim                 (soft adapter)
 ├── spectrumx-ai-ran-gary              (soft adapter)
 ├── readygary-6g-beam-selection        (optional metrics)
 ├── gunnchos-hardware-industrial-design (Gate 6 HW)
 └── gunnchos-device-os                (Gate 6 OS)
```

## Risk register

| Risk | Mitigation |
|---|---|
| CUDA unavailable | Portable CPU pass; GPU pending truthful |
| Docker unavailable | Native bootstrap paths documented |
| Legacy gate name collision | Namespace `GATES_4_6_*` |
| spectrumx detached HEAD | Branch from current commit; record in lock |
| Empty new repos | Initial commits on feature branch |
