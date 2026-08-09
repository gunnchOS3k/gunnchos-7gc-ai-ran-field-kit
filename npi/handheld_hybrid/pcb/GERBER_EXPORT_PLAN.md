# Gerber / drill export plan — Handheld Hybrid

Updated: 2026-08-08T20:15:00Z  
PHYSICAL_EXECUTION_FREEZE ACTIVE — **no fab**.

## Intended CLI (when kicad-cli available)
```bash
kicad-cli pcb export gerbers device_designs/handheld_hybrid/kicad/handheld_hybrid.kicad_pcb \
  -o device_designs/handheld_hybrid/manufacturing/gerbers/
kicad-cli pcb export drill device_designs/handheld_hybrid/kicad/handheld_hybrid.kicad_pcb \
  -o device_designs/handheld_hybrid/manufacturing/gerbers/
kicad-cli pcb export pos device_designs/handheld_hybrid/kicad/handheld_hybrid.kicad_pcb \
  --side both --format csv -o device_designs/handheld_hybrid/manufacturing/pick_place.csv
```

## Status
- `kicad-cli`: **ABSENT** → `EDMUND_ACTION_REQUIRED`
- SoM: **Radxa NX5 RM121-D8E32** (public pinout available — nets must cite PUBLIC_PINOUT)

## Non-claims
No fab-ready Gerbers.
