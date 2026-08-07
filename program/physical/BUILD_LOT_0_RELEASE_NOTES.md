# Build Lot 0 — Release Notes (EVT)

Updated: 2026-08-07T23:39:45Z

## Classification

**EVT / engineering validation / Build Lot 0** — not production.

## Purpose

Freeze the digital design baseline so physical construction and Gate 1–2 evidence capture can begin after Edmund releases the freeze.

## Digital baseline pins

See `PHYSICAL_BASELINE_VERSION_LOCK.yaml`.

## Minimal first physical set

1. Edge I/O Ring PCB (fab from digital package) + printed enclosure
2. Ring assembly + SWD flash of DEVELOPMENT firmware
3. One representative device OS boot target
4. Dock cable / continuity path
5. Local gunnchAI3k host (existing PC/laptop acceptable for Lot 0)
6. One game runtime target (Beat Link or Anime Aggressors)

## Non-goals

- No Gate 4 human pilot in Lot 0
- No carrier/certification
- No production signing keys
- No purchase automation (Edmund places orders)

## Safety

Follow `MASTER_BRINGUP_SEQUENCE.md` current limits. Li-ion handling requires human supervision.
