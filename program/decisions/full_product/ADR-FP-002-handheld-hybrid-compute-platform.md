# ADR-FP-002 — Handheld Hybrid compute platform freeze

- Status: **ACCEPTED (engineering baseline)**
- Date: 2026-08-08T00:07:41Z

## Decision
**Selected:** Rockchip **RK3588S** (4×A76 + 4×A55, Mali-G610 MP4, 6 TOPS NPU class) with 16 GB LPDDR4x, 256 GB UFS 3.1.

Rationale: handheld thermal/battery envelope; equity cost; adequate Godot/Vulkan path; dock provides Desktop-class expansion via USB3/DP rather than claiming USB4 80G.

## Frozen specs
- Display: 7" class 1920×1080 IPS, 120 Hz capable, capacitive touch
- Controls: dual sticks + ABXY + L/R + triggers + D-pad (exact switch module MPNs in BOM)
- Radios: Wi-Fi 6E/BT 5.3 module (AIC8800D or AP6275P class — freeze MPN in BOM)
- WWAN: optional shared M.2 WWAN with Student family modem where thermal allows; otherwise Wi-Fi-first SKU
- Battery: 5000–6000 mAh 1S2P or 2S pack with protection
- USB-C: USB 3.2 Gen1 + DP Alt Mode + PD sink/source for dock
- Security: secure element footprint (NXP SE050) + verified boot path in gunnchOS

## Continuity
Dock transition must preserve apps/saves/identity/network/AI-privacy/input/display/audio — tested by `gunnchos-device-os` continuity suite (expand to FULL).
