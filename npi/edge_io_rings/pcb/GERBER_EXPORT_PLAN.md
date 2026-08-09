# Gerber / drill export plan — Edge I/O Rings

Updated: 2026-08-08T20:15:00Z  
PHYSICAL_EXECUTION_FREEZE ACTIVE — **no fab**.

## Intended CLI (when kicad-cli available)
```bash
kicad-cli pcb export gerbers device_designs/edge_io_rings/kicad/edge_io_rings.kicad_pcb \
  -o device_designs/edge_io_rings/manufacturing/gerbers/
kicad-cli pcb export drill device_designs/edge_io_rings/kicad/edge_io_rings.kicad_pcb \
  -o device_designs/edge_io_rings/manufacturing/gerbers/
kicad-cli pcb export pos device_designs/edge_io_rings/kicad/edge_io_rings.kicad_pcb \
  --side both --format csv -o device_designs/edge_io_rings/manufacturing/pick_place.csv
```

Also sync gate1 path when CLI present: `gate1_digital_fabrication/edge_io_ring/`.

## Status
- `kicad-cli`: **ABSENT** → `EDMUND_ACTION_REQUIRED`
- MCU: **nRF52840-QIAA-R**
- Fusion CAD binary `.f3d` still needs Edmund Fusion authoring

## Non-claims
No fab-ready Gerbers / no physical ring boot.
