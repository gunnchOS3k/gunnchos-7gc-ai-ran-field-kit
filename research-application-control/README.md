# Research Application Control Plane

Authoritative gate status and acceptance tooling for the gunnchOS3k PhD research portfolio.

## Commands

```bash
make verify-repo-lock
make application-readiness
python3 scripts/validate_master_status.py
python3 scripts/validate_preregistration.py
python3 scripts/validate_application_packet.py
```

## Truth rules

- Never mark a gate PASS without genuine evidence files listed in `MASTER_STATUS.json`.
- Synthetic fixtures never count as Gate 3.
- Calibration and rehearsal never count as pilot evidence.
- Edmund retains merge authority for all PRs.
