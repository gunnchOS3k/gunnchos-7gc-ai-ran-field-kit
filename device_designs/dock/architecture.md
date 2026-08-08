# Architecture — First-party Dock

**Status:** DIGITAL_DESIGN / FULL_PRODUCT  
**ADR:** ADR-FP-006  
**Updated:** 2026-08-08T00:50:00Z  
**Manufacturing:** skeleton toward package — **no fab**

USB4 40 Gbps path for Student/DS-XL; USB3+DP path for Handheld.
Hosts ring charging cradle / optional UWB companion assist (`UWB_ON_COMPANION` per ADR-FP-008).
No certification logos / USB-IF claims.

## Subsystems
- Power tree: AC adapter → PD sink/source → internal rails (see `electrical/power_tree.yaml`)
- USB4 / hub / Ethernet / display egress (ICD)
- Mechanical enclosure params (skeleton)
- Fab notes skeleton (Gerber/BOM/assembly placeholders)
- Continuity via existing `dock_manager` software path
