# Interface Control Document — First-party Dock

**Device:** `dock`  
**ADR:** ADR-FP-006  
**Updated:** 2026-08-08T00:50:00Z  
**Evidence class:** MODELED — no certification claims

## Hosts
| Host | Upstream path | Max power negotiated |
|---|---|---|
| student_14_5 | USB4 40 Gbps (JHL9040 class) | up to 100 W PD |
| ds_xl_coder | USB4 40 Gbps | up to 100 W PD |
| handheld_hybrid | USB 3.2 + DP Alt (VL108 cost-down OK) | up to 65 W PD |
| edge_io_rings | Charge cradle pogo + optional UWB assist | ≤100 mA @ 5 V charge |

## External ports
| Port | Signal | Notes |
|---|---|---|
| USB-C upstream | USB4 / USB3 / PD | To host device |
| USB-C DS ×2 | USB3 + PD/DP as silicon allows | Downstream peripherals |
| USB-A 3.2 ×2 | Via VL817 | Legacy peripherals |
| HDMI 2.1 or DP 1.4 ×1 | Display egress | Retimer TBD AVL |
| RJ45 | 2.5GbE via RTL8156 | RTL8153 cost-down |
| Ring cradle pogo ×2 | CHARGE_5V + GND | Keyed polarity; ESD required |
| UWB antenna (optional) | RF | Only if U8 populated |

## Non-claims
No measured eye diagrams, no FCC/CE, no production ICD freeze.
