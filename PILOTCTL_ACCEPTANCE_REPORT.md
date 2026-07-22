# PILOTCTL_ACCEPTANCE_REPORT

Generated: 2026-07-22T18:30:03Z

## Result

**PASS** (fixture-based acceptance; 8/8 dedicated tests + full suite green)

## Checks

| Check | Result |
|---|---|
| Matrix has exactly 54 cells | PASS |
| Calibration cannot satisfy a cell | PASS |
| Synthetic cannot satisfy a cell | PASS |
| Wrong zone rejected | PASS |
| Withdrawn rejected | PASS |
| Privacy-fail rejected | PASS |
| next-cell deterministic | PASS |
| Status shows 0 eligible with calibration present | PASS |

Commands:

```
python3 -m pytest -q tests/pilotctl
python3 scripts/pilotctl.py status
python3 scripts/pilotctl.py next
```
