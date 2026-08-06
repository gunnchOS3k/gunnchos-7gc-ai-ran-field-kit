# Acceptance-Completion Initial Audit

**Timestamp:** 2026-07-29T21:10:00Z (session)  
**Host:** Apple M2 — no NVIDIA GPU  
**Rule:** statuses below are audit baseline, not earned PASSes unless validators say so

## Truthful baseline (until validators pass)

```text
CONTROL_PLANE_IMPLEMENTED_BUT_REMOTE_CI_RED
GATE4_OULU_FUNCTIONAL_SCAFFOLD_PASS
GATE4_OULU_PILOT_EVIDENCE_PASS
GATE4_OULU_SCIENTIFIC_EVIDENCE_PENDING
GATE4_NVIDIA_EDUCATIONAL_CPU_PASS
GATE4_NVIDIA_NR_STYLE_SCAFFOLD_PASS
GATE4_NVIDIA_AERIAL_DEPTH_PENDING
GATE4_NVIDIA_GPU_PENDING
GATE5_DRAFT_PACKAGE_PASS
GATE5_PUBLICATION_RELEASE_PENDING
GATE6_PARTIAL_HARNESS_PASS
GATE6_PHYSICAL_EVIDENCE_PENDING
NO_ACCEPTANCE_GUARANTEE
```

## Repository snapshot (start of acceptance pass)

| repository | default | local branch | HEAD | notes |
|---|---|---|---|---|
| gunnchos-7gc-ai-ran-field-kit | master | cursor/field-kit-remote-integrity-release | `de818fb` (master merge of #11) | App Readiness + Gate2 RED on master |
| gunnchos-emergent-service-intent-protocols | main | cursor/oulu-publication-grade-science | `9b3fec9` (PR #1 merged) | pilot science on main; final pending |
| gunnchos-gpu-nr-baseband-platform | main | cursor/nvidia-real-nr-aerial-depth | `770bb21` (PR #1 merged) | educational CPU + scaffold NR; Aerial depth pending |

Supporting siblings remain at prior Gate6 harness SHAs (see `integration/repo-lock.json`).

## Remote CI (master push after #11)

| workflow | run | conclusion | failing step |
|---|---|---|---|
| Application readiness CI | 30489513914 | failure | Checkout locked sibling repositories |
| Gate 2 Integrated System | 30489512237 | failure | Schema and failure tests (provenance) |
| Gate 3 Evidence Readiness | — | success | — |
| Gate 4 Evaluation Readiness | — | success | — |
| Umbrella Artifact CI | — | success | — |

Root causes (see `REMOTE_CI_FAILURE_REPRODUCTION.md`):

1. Private Oulu/NVIDIA clones without GitHub App / token → exit 128.
2. Lock requires Oulu/NVIDIA/hardware/device-os; Gate2 workflow only checks out the original five siblings; provenance match/dirty tests fail on Ubuntu runner.

## Planned tracks

- **A** Field-kit remote integrity (App token checkout, lock tests, mandatory workflows, branch protection handoff)
- **B** Oulu publication-grade science (semantic causality, E2E DIAL/TarMAC, final matrix)
- **C** Real NR BG1/BG2 + independent refs + CUDA depth
- Gate 5 RC readiness without fabricating DOI/independent/physical completion
