# EVT Physical Test Book — Cont IX (procedures before boards exist)

Updated: 2026-08-09T20:50:52Z  
PHYSICAL_EXECUTION_FREEZE — procedures only; no physical execution.

## 1. Incoming inspection
- Verify silk rev `0.6.0-cont-ix`, panelization marks, impedance coupons present.

## 2. Power bring-up
- TP: GND, VBUS, VSYS, 3V3 sequence; current limit supply.

## 3. Programming
- Per-product PROGRAMMING.md; record FW hashes.

## 4. Interfaces
- USB enumeration, display light-up, radio smoke (Ring), Ethernet (Dock).

## 5. Thermal soak
- Idle/load temperature map — limits TBD from thermal model (EXTERNAL chamber cal).

## 6. Failure logging
- Use issue template `EVT_ISSUE_TEMPLATE.md`.
