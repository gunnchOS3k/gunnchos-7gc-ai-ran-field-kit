# Gate 3 Pilot Operator Guide

This guide supports controlled physical collection. Do not prefill fake measurements.

## Before Day 1

- Review `protocols/CONTROLLED_PILOT_PROTOCOL.md`.
- Confirm consent language and deletion workflow.
- Run `make pilot-status` and confirm no synthetic/calibration sessions are counted.
- Prepare devices without raw GPS, SSIDs, BSSIDs, serials, phone numbers, email addresses, or other direct identifiers.

## Day 1 checklist

- Run `make pilot-next`.
- Collect only the indicated matrix cells.
- Validate each session locally with `python3 scripts/validate_session.py --input <session>`.
- Import with `make pilot-import SESSION=<session>`.

## Day 2 checklist

- Re-run `make pilot-status`.
- Continue pending cells from `make pilot-next`.
- Check duplicate/consent/privacy failures before re-collection.
- Run `make pilot-validate-day DAY=day_02` after imports.

## Day 3 checklist

- Complete remaining matrix cells.
- Run `make pilot-validate-day DAY=day_03`.
- Run `make pilot-report`.
- Review rejected sessions before assembling a controlled dataset.

## Safety rules

- Synthetic or `calibration_only` sessions never count toward the pilot.
- Emulator provenance cannot be relabeled as physical evidence.
- Withdrawn, deleted, inactive-consent, duplicate-hash, or privacy-finding sessions are rejected.
