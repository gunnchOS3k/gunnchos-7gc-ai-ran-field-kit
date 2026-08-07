# Architecture — Student 14.5

**Status:** DIGITAL_DESIGN / NONPHYSICAL  
**Physical:** `REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING`  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE

## Role
classroom laptop/tablet hybrid, 14.5-inch class display

## Subsystems
- Mechanical enclosure (parameterized CAD)
- Electrical power + I/O
- Application processor / MCU and firmware
- OS integration profile
- Manufacturing package (candidate)
- Validation harnesses (sim + collectors for later MEASURED)

## Trust boundary
Root of Trust → bootloader → OS kernel → signed update client → apps/games.

## Non-claims
This package does **not** claim physical build, FCC/CE, or `GATE_2_PASS`.
