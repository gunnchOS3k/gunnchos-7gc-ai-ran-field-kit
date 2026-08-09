# Gerber / drill export plan — Student 14.5

Updated: 2026-08-08T20:15:00Z  
PHYSICAL_EXECUTION_FREEZE ACTIVE — **no fab**.

## Intended CLI (when kicad-cli available)
```bash
kicad-cli pcb export gerbers device_designs/student_14_5/kicad/student_14_5.kicad_pcb \
  -o device_designs/student_14_5/manufacturing/gerbers/
kicad-cli pcb export drill device_designs/student_14_5/kicad/student_14_5.kicad_pcb \
  -o device_designs/student_14_5/manufacturing/gerbers/
kicad-cli pcb export pos device_designs/student_14_5/kicad/student_14_5.kicad_pcb \
  --side both --format csv -o device_designs/student_14_5/manufacturing/pick_place.csv
```

## Status
- `kicad-cli`: **ABSENT** → `EDMUND_ACTION_REQUIRED`
- `gerbers/` intentionally empty (no fake Gerber geometry)
- Compute: **ADLINK COM-HPC-mMTL-155H-32G**

## Non-claims
No Gerber zip is fab-ready until ERC/DRC + real footprints.
