# Manufacturing release package checklist — handheld_hybrid

Updated: 2026-08-08T20:58:59Z  
PHYSICAL_EXECUTION_FREEZE — checklist is digital readiness only.

- [x] Assembly BOM with exact preferred MPNs
- [x] Stackup YAML
- [x] Fab notes
- [x] Netlist JSON (Cont VI)
- [x] Pick/place plan (plan-only coordinates OK under freeze)
- [x] Gerber export plan (no fake gerbers)
- [x] STEP export status (blocked on CLI/CAD where noted)
- [x] ERC/DRC status JSON (NOT_RUN until kicad-cli)
- [ ] Actual Gerber/drill/PnP/STEP from kicad-cli — **resume when CLI ready**
- [ ] Fab PO / purchase — **FORBIDDEN under freeze**

Completeness token for this product: digital package deepened; fabrication exports pending CLI.
