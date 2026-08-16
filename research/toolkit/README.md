# Researcher toolkit scaffolding (STREAM-C-PKT-001 / C7)

Honest adapters for **new** digital experiments and **reproduce** workflows.
Does not claim physical validation, SoA, or STANDARDIZED_6G.

## Layout

- `research/new/` — scaffold a packet skeleton (PROBLEM/METHOD/METRICS + runner stub)
- `research/reproduce/` — replay registered seeds / write raw digests for a packet
- `research/toolkit/` — shared CLI entrypoints

## Commands

```bash
python3 -m research.toolkit.new_packet --packet R6G-0XX --title "..."
python3 -m research.toolkit.reproduce_packet --packet R6G-006 --out artifacts/r6g/replication
make r6g-reproduce   # full portfolio (preferred)
```

## Claim boundary

- IMPROVED_STATE_OF_ART = false unless earned externally
- PHYSICAL / COMPLIANT / STANDARDIZED_6G never emitted by these adapters
- New packets start at MODELED or DIGITALLY_EXECUTED only after real seeded runs
