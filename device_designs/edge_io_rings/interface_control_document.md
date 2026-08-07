# ICD — Edge I/O Rings

| Interface | Direction | Protocol | Notes | Evidence |
|---|---|---|---|---|
| USB-C data/power | bidirectional | USB 2.0/3.x + PD candidate | dock/host | MODELED |
| BLE | bidirectional | BLE 5.x | ring/host | MODELED |
| Wi-Fi | bidirectional | 802.11ac/ax candidate | fleet | MODELED |
| Display panel | SoC→panel | MIPI-DSI / eDP candidate | HAL mock | NONPHYSICAL |
| Secure boot OTP/fuse | RoT→boot | vendor RoT API | emulator | SIMULATED |
| Update channel | host→device | signed bundle v1 | adapters | SOFTWARE |
| NTN modem slot | optional | abstracted bearer | no real NTN claim | ABSTRACTED |

Physical connector mating and RF chamber results: `PHYSICAL_PENDING`.
