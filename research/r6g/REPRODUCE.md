# R6G Digital Replication — Reproduce Guide

## Scope

This reproduces **digital** R6G experiments only (R6G-003 / 005 / 009 active replication candidates, plus spectrum fabric and semantic continuity supporting packets).

It does **not** claim:

- `IMPROVED_STATE_OF_ART`
- physical / OTA beat of published baselines
- external or peer-reviewed validation
- standardized 6G compliance

## Quick start

```bash
make r6g-reproduce
```

Equivalent:

```bash
python3 -m research.r6g.replication.reproduce
python3 -m research.r6g.replication.verify_independent
python3 -m pytest tests/test_r6g_breakthroughs.py tests/test_r6g_replication.py -q
```

## Outputs

| Path | Meaning |
|------|---------|
| `artifacts/r6g/replication/raw/` | Per-seed / per-run raw JSON |
| `artifacts/r6g/replication/R6G_REPLICATION_SUITE.json` | Aggregate suite + claim states |
| `artifacts/r6g/replication/R6G_NEGATIVE_RESULTS.json` | Preserved negatives |
| `artifacts/r6g/replication/R6G_PORTFOLIO_DASHBOARD.json` | Honesty dashboard |
| `artifacts/r6g/replication/R6G_INDEPENDENT_VERIFIER.json` | Recalculated-from-raw check |
| `artifacts/r6g/replication/SEED_REGISTRY.json` | Pre-registered seeds |

## Seed registry

Seeds are pre-registered in `research/r6g/replication/seed_registry.py`. Do not cherry-pick seeds after seeing outcomes. Amendments require an entry in `amendments`.

## Independent verification

`verify_independent` recalculates primary metrics from raw modality matrices / result tables. It does not trust author-side summary fields alone.

## Claim states

Allowed: `PROMISING_DIGITAL`, `DIGITAL_IMPROVEMENT_CANDIDATE`, `NEGATIVE_RESULT_DOCUMENTED`, `REPLICATION_INCOMPLETE`, …

Forbidden: `BREAKTHROUGH_PROVEN`, `STATE_OF_ART_SURPASSED`, physical/external/peer-reviewed PASS without evidence.

## Deferred

Large Sionna/ns-3/DeepMIMO sweeps, multi-hour RF, extra QEMU, THz/RIS hardware purchase.
