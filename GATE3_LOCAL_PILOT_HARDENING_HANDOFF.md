# GATE3_LOCAL_PILOT_HARDENING_HANDOFF

This handoff prepares **local** Android / operator work. It does not implement
device hardware behavior in the cloud environment.

## Current truthful Gate 3 state

| Field | Value |
|---|---|
| Status | `GATE3_PARTIAL_EVIDENCE` |
| Eligible pilot sessions | 0 |
| Completed cells | 0 |
| Missing cells | 54 |
| Pixel calibration | valid, calibration_only, excluded from pilot |
| External evidence | `EXTERNAL_EVIDENCE_PASS` (NTN / TR 38.821) |

## Current Android limitations (to harden locally)

- 60-second calibration duration is hard-coded in the production UI path
- run IDs use calibration naming (`pixel-cal-…`)
- network type can be hard-coded in export paths
- location category can be hard-coded
- collection-day metadata is incomplete for pilot assignment
- environmental context is not fully operator-controlled
- pilotctl is not yet directly bound to an Android pilot assignment
- the app must prevent calibration metadata from entering pilot cells

## Required local implementation modes

### Calibration mode

- duration: **60 seconds**
- `calibration_only = true`
- zone: `zone_calibration`
- excluded from pilot matrix
- run-ID prefix: `pixel-cal-` or `cal-`

### Pilot rehearsal mode

- duration: **300 seconds**
- `rehearsal_only = true`
- excluded from pilot counting
- uses the pilot UI and assignment contract
- run-ID prefix: `rehearsal-`

### Pilot mode

- duration: **300 seconds**
- `calibration_only = false`
- `rehearsal_only = false`
- `collection_day_id`: `day_01` | `day_02` | `day_03`
- zone: `zone_a` | `zone_b` | `zone_c`
- workload: `learn` | `create` | `sense`
- selected authorized network condition
- pilot cell ID present and matching matrix
- run-ID prefix: `pilot-`
- accurate detected network transport (not hard-coded when APIs expose it)
- full coarse environmental context (no exact addresses)

## Interface contracts already available

- `contracts/measurement_session_context.v1.schema.json`
- `protocols/controlled_pilot_matrix.csv`
- `scripts/pilotctl.py` (`status`, `next`, `import-session`, `validate-day`, `report`)
- Gate 3 status evaluator rejects calibration_only for pilot eligibility

## Success criteria for local hardening

1. Calibration exports cannot map to any of the 54 pilot cells.
2. Pilot exports require day/zone/network/workload matching an open cell.
3. Rehearsal exports are rejected for pilot counting.
4. Consent remains manual / affirmative (never adb-tapped).
5. Privacy scan remains recursive and fails closed.

## Non-goals for this cloud handoff

- USB / ADB / wireless-debug pairing
- committing raw or private sanitized measurement JSON
- starting the 54-session pilot automatically
