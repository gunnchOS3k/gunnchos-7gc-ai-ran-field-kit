# GATE3_PILOT_MODE_BASELINE_AUDIT

Generated after synchronizing merged Gate 1 / taxonomy defaults and creating
pilot-hardening branches.

## Local preflight

| Field | Value |
|---|---|
| Host | macOS 26.5.2 (Darwin 25.5.0, arm64) |
| User | gunnchos |
| adb | DEVICE_AUTHORIZED |
| Pixel | Pixel 6a |
| Android | 17 (API 37) |
| Serial | omitted from research artifacts |

## Repository manifest

`/tmp/gunnchos_gate3_pilot_repo_manifest.json`

## Merged defaults (authoritative)

| Repo | Default | SHA |
|---|---|---|
| edge-io-measurement-node | main | `764192f` (includes merged PR #22) |
| gunnchos-7gc-ai-ran-field-kit | master | `ffb237fb29a77f68fe2185b6d72de33edc076748` (Gate 1 PR #6) |
| 7gc-digital-twin | main | `fcc9b11` (null-metrics fix on main) |
| spectrumx-ai-ran-gary | main | `f7af6c7` |
| ntn-resilience-sim | main | `2403456` |

Field-kit contains merge commit `ffb237f` (exact HEAD at branch creation).

## Working branches

| Repo | Branch |
|---|---|
| edge-io | `cursor/gate3-pilot-mode-hardening` |
| field-kit | `cursor/gate3-pilot-assignment-controller` |

## Baseline verification

| Check | Result |
|---|---|
| `validate_gate1_thesis.py` | GATE_1_PASS |
| `make verify-repo-lock` | PASS (after NTN returned to locked main) |
| field-kit `pytest` (pilotctl) | PASS |
| `make gate4-evaluation-ready` | GATE4_EVALUATION_READY |
| edge-io Python `pytest` | 18 passed |

## Gate status entering this work

- Gate 1: GATE_1_PASS
- Gate 2: GATE2_SYSTEM_PASS
- Release evidence: RELEASE_EVIDENCE_PENDING
- Gate 3: GATE3_PARTIAL_EVIDENCE
- Gate 4: GATE4_EVALUATION_READY
- Pilot coverage: 0 / 54

## Blocking limitations addressed by this branch

1. Typed CALIBRATION / PILOT_REHEARSAL / PILOT modes (60s vs 300s).
2. Versioned `gunnchos.pilot_assignment` contract + pilotctl emit/validate.
3. Android document-picker assignment import with hash verification.
4. Declared network condition vs detected transport separation.
5. Explicit rehearsal exclusion from the 54-session matrix.
