# Gerber / drill export plan — Dock

Updated: 2026-08-08T20:15:00Z  
PHYSICAL_EXECUTION_FREEZE ACTIVE — **no fab**.  
Architecture freeze: **USB4 / TB4 @ 40 Gbps** (ADR-HW-002) — **not TB5**.

## Intended CLI (when kicad-cli available)
```bash
kicad-cli pcb export gerbers device_designs/dock/kicad/dock.kicad_pcb \
  -o device_designs/dock/manufacturing/gerbers/
kicad-cli pcb export drill device_designs/dock/kicad/dock.kicad_pcb \
  -o device_designs/dock/manufacturing/gerbers/
kicad-cli pcb export pos device_designs/dock/kicad/dock.kicad_pcb \
  --side both --format csv -o device_designs/dock/manufacturing/pick_place.csv
```

## Status
- `kicad-cli`: **ABSENT** → `EDMUND_ACTION_REQUIRED`
- Controller: **JHL8440**; retimer: **JHL9040R**; forbidden: JHL9480/JHL9580

## Non-claims
No fab-ready Gerbers; no USB-IF / Thunderbolt logo.
