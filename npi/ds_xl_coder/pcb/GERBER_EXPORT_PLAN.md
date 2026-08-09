# Gerber / drill export plan — DS-XL Coder

Updated: 2026-08-08T20:15:00Z  
PHYSICAL_EXECUTION_FREEZE ACTIVE — **no fab**.

## Intended CLI (when kicad-cli available)
```bash
kicad-cli pcb export gerbers device_designs/ds_xl_coder/kicad/ds_xl_coder.kicad_pcb \
  -o device_designs/ds_xl_coder/manufacturing/gerbers/
kicad-cli pcb export drill device_designs/ds_xl_coder/kicad/ds_xl_coder.kicad_pcb \
  -o device_designs/ds_xl_coder/manufacturing/gerbers/
kicad-cli pcb export pos device_designs/ds_xl_coder/kicad/ds_xl_coder.kicad_pcb \
  --side both --format csv -o device_designs/ds_xl_coder/manufacturing/pick_place.csv
```

## Status
- `kicad-cli`: **ABSENT** → `EDMUND_ACTION_REQUIRED`
- Compute: **ADLINK COM-HPC-mMTL-155H-32G** (shared with Student; dual-eDP is carrier)

## Non-claims
No fab-ready Gerbers.
