# Repair procedures (NONPHYSICAL manuals)

## Safety
Power off, disconnect battery connector before board work. ESD precautions.

## Student 14.5 / Handheld Hybrid / DS-XL Coder
1. Identify FRU from `component_bom.csv`.
2. Follow torque map in manufacturing notes (candidate).
3. Re-run secure boot verify + signed update health check in emulator before physical return-to-service.
4. Physical reassembly validation: `PHYSICAL_PENDING`.

## Edge I/O Rings
1. Do not attempt coin-cell replacement under freeze without procurement release.
2. Pairing reset via host simulator `pair()` after battery service.
3. Recalibrate; confirm fallback modes clear.

## Claims
These are procedures and manuals only. No field repair completion claimed.
