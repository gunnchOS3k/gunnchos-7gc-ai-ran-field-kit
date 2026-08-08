# Dock — Fabrication notes (skeleton)

**Device:** `dock`  
**Updated:** 2026-08-08T00:50:00Z  
**Status:** MANUFACTURING_PACKAGE_SKELETON  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE — **no fab release**

## Intent
Skeleton toward a manufacturing package (Gerbers, BOM, assembly, test). Not an RFQ release.

## Expected package contents (when design exists)
1. `gerbers/` — IPC-2581 or RS-274X + drill
2. `bom/assembly_bom.csv` — AVL with preferred + alternates
3. `pick_place.csv` — centroid
4. `stackup.yaml` — controlled impedance for USB4 / HDMI
5. `test/ict_boundary.md` — ICT/flying probe + PD contract tests
6. `mechanical/` — STEP + enclosure drawings
7. `compliance/pre_scan_notes.md` — FCC/CE prep (no logos)

## Blockers before fab
- `DESIGN_PENDING` main PCB in KiCad
- AVL quotes for JHL9040 / display retimer
- Edmund ACCEPT for any physical build lot
- No fab from this skeleton alone
