# EVT Acceptance Matrix — Student 14.5

Source: hardware `artifacts/continuation_ix_pre_evt/evt/EVT_PHYSICAL_TEST_BOOK.md`  
Policy: unknown safety/performance thresholds = `TARGET_TO_CONFIRM` (never invent).

| Test ID | Stage | Procedure | Limit | Limit source | Pass criteria |
|---|---|---|---|---|---|
| EVT-IN-01 | EVT0 | Incoming silk/rev/panelization/impedance coupons | Match `STUDENT145-EVT0-R0` | release_manifest | All match |
| EVT-PWR-01 | EVT0 | Power bring-up TP sequence | TARGET_TO_CONFIRM | power tree OEM | No overcurrent trip at set limit |
| EVT-PRG-01 | EVT0 | Programming + FW hash | Hash match release | programming log | Recorded hash |
| EVT-IF-01 | EVT0 | USB enumerate / display / radio smoke | Enum OK | interface smoke | Functional smoke PASS |
| EVT-TH-01 | EVT1 | Thermal soak idle/load | TARGET_TO_CONFIRM | thermal model EXTERNAL | Data logged; no invent limits |
| EVT-RF-01 | EVT1 | RF conducted/radiated pre-scan | TARGET_TO_CONFIRM | lab procedure | Report filed; no CERTIFIED claim |
| EVT-BAT-01 | EVT1 | Battery charge/discharge | TARGET_TO_CONFIRM | pack OEM | Within OEM profile |
| EVT-MECH-01 | EVT1 | Hinge/flex cycle sample | TARGET_TO_CONFIRM | hinge OEM | No opens; OEM life TBD |
