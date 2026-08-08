# ADR-FP-006 — First-party Dock product freeze

- Status: **ACCEPTED (engineering baseline)**
- Date: 2026-08-08T00:07:41Z

## Decision
Create Dock as first-party product `device_designs/dock/`.

### Baseline silicon
- USB4/TBT dock controller: **Intel JHL9040 / Maple Ridge class** OR cost-down **USB 3.2 + DP Alt hub** (**VL107/VL108 class**) for Handheld-first; Student/DS-XL target USB4 40 Gbps path
- PD controller: **Texas Instruments TPS65994** class
- Ethernet: **Realtek RTL8153/RTL8156** GbE/2.5GbE
- USB hub: **VL817** class for downstream USB-A
- Audio: ALC4050 class USB audio optional

### Ports
- 1× upstream USB-C to device
- 2× USB-C downstream (DP/USB)
- 2× USB-A 3.2
- 1× HDMI 2.1 or DP 1.4
- 1× RJ45
- 1× 3.5mm optional
- PD source up to 100W negotiated (profile must match selected silicon)

### Software
Continuity via existing `dock_manager` — expand automated continuity suite.
No USB-IF logo claims before certification.
