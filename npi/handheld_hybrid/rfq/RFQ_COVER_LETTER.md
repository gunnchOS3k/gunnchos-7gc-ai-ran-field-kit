# RFQ Cover Letter — Handheld Hybrid (DRAFT — DO NOT SEND)

Generated: 2026-08-09T22:00:34Z

CONFIDENTIAL — gunnchOS3k internal / Edmund review only. Do not redistribute.
PHYSICAL_EXECUTION_FREEZE ACTIVE. This packet is for Edmund review only.
No purchase. No fab. No NDA accept by Cursor.

## Scope
Quote EVT0/EVT1 PCBA (+ box-build optional) for `handheld_hybrid` config `HHYBRID-EVT0-R0`.

Compute: Radxa NX5 RM121-D8E32
Manufacturer token (Cont IX): `HANDHELD_HYBRID_MANUFACTURER_PACKAGE_READY`

## Attachments (in this package)
- `RELEASE_MANIFEST.json`
- `QUOTE_READY_BOM.csv`
- `DFM_PRECHECK.md`
- `ASSEMBLY_WORK_INSTRUCTION.md`
- `PROGRAMMING.md`
- `PCB_PACKAGE_INDEX.json`
- `VENDOR_COLLATERAL_REQUESTS.json`

## Hardware gerbers (accepted tip)
See `pcb/PCB_PACKAGE_INDEX.json` → hardware repo `cont_ix_release/` at accepted tip SHA
`8705f5a25065e02c7513e990a43e4762967906c5` (Cont IX manufacturing lock `cd1d906c5f08eb26c350851a4faeb05e2bf2e79f`; gerber/PnP/STEP/drill hashes unchanged).

## Explicit non-goals
- Not authorizing fabrication
- Not Thunderbolt 5 (Dock uses JHL8440 + JHL9040R)
- Not claiming host carrier certification


## Known open NPI defect (must disclose to vendor / Edmund)
- `NPI_DEFECT-HANDHELD-STORAGE-HEADROOM-001` — preferred RM121-D8E32 32GB eMMC operational headroom is OPERATIONALY_UNSAFE for Phase XIV/XV reduced profile (usable_free≈−1.74GB).
- WP-002 ACTIVE; hardware #53 merged policy recommendation (system eMMC + enforced external/user-media). Does **not** invent larger undocumented NX5 SKUs.
- `blocks_rfq_send=false` / `blocks_purchase=false`, but defect must not be hidden. Quote may assume current SoM MPN with storage-policy caveat.
- Evidence: `program/frontier_parity/phase_xv/HANDHELD_STORAGE_DECISION.json`
