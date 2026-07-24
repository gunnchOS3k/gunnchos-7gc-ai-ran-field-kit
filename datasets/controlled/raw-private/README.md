# Raw Private Device Exports

This directory holds **local-only** raw device measurement exports.

## Git policy

All files here are **gitignored** except:

- `.gitkeep`
- `README.md`

Never commit raw session JSON, device identifiers, or unreviewed payloads.

## Workflow

1. Collect under PILOT/CALIBRATION/REHEARSAL modes per `pilot/PILOT_PROTOCOL_v1.md`
2. Store exports here with session manifest references
3. Run privacy scan before any copy to `sanitized/`
4. Log provenance in `RAW_TO_SANITIZED_PROVENANCE.json` after sanitization (human-approved)

## Status

At scaffold freeze: directory empty — **0/54** pilot cells complete.
