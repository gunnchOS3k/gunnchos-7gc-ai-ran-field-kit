# Block diagram — Handheld Hybrid

```mermaid
flowchart LR
  subgraph handheld_hybrid[Handheld Hybrid]
    PWR[Power/Battery] --> PMIC[PMIC]
    PMIC --> SOC[SoC/MCU]
    SOC --> DISP[Display/UI]
    SOC --> IO[I/O Ports]
    SOC --> RF[WiFi/BT/NTN-ready]
    SOC --> SEC[RoT / Secure Element]
    IMU[Sensors/IMU] --> SOC
  end
  HOST[Host / Fleet] <--> RF
```

