# Edmund — Build Lot 0 Human Actions

Updated: 2026-08-07T23:39:45Z

Only actions software cannot perform. Cursor runs all command-line work.

## H0 — Approve macOS admin for KiCad (if still needed)

- **Action:** Approve macOS administrator/install prompt for Homebrew KiCad cask
- **Why human:** sudo/GUI authorization
- **Safety:** Official KiCad cask only
- **Before (Cursor):** attempted `brew install --cask kicad`; static ERC/DRC already PASS
- **After (Cursor):** run kicad-cli ERC/DRC/Gerber; record `RING_KICAD_CLI_VALIDATION_PASS`
- **Evidence:** CLI validation report + hashes

## H1 — Place parts order (after freeze release)

- **Action:** Place order from quote-ready BOM (`MASTER_PROCUREMENT_BOM.csv`)
- **Why human:** payment / contractual acceptance
- **Do not:** accept unknown license/export terms without review
- **After:** Cursor updates receiving checklist

## H2 — Receive / incoming inspection

- **Action:** Open packages; photograph packing slips; count against BOM
- **Evidence:** photos + filled inspection form

## H3 — PCB fab / enclosure print handoff

- **Action:** Submit Gerbers/STEP to fab/print house OR receive boards/prints
- **Digital package:** hardware `gate1_digital_fabrication/edge_io_ring/`

## H4 — Ring assembly / soldering

- **Action:** Assemble SMT/through-hole per assembly sequence
- **Safety:** ESD, eye protection, fume extraction

## H5 — Physical flash / button / cable plug

- **Action:** Connect SWD probe; power board; press reset; plug USB-C dock path
- **After:** Cursor captures serial logs / evidence schemas (no PASS claim without Edmund review)

## H6 — Play real game loop on device

- **Action:** Run Beat Link / Anime / Pedestrian / Archive on physical target
- **Evidence:** screen recording + checklist; Edmund accepts/rejects

## H7 — Accept/reject evidence

- **Action:** Review evidence packs; set Gate 1/2 physical PASS or FAIL
- **Authority:** Edmund Gunn Jr. final
