# ADR-FP-001 — Student 14.5 compute platform freeze

- Status: **PROPOSED → ACCEPTED (engineering baseline)**
- Date: 2026-08-08T00:07:41Z
- Deciders: Cursor (engineering baseline); Edmund remains final product-scope authority

## Context
Full-product mode forbids vague `SoC_application_processor` BOM lines.
Student 14.5 must sustain academic sessions, local AI, full games, docking, multi-display, offline operation.

## Options evaluated
intel_core_ultra_7_155H:
  score_sum: 219
  cpu: 9
  gpu: 8
  npu: 8
  perf_per_watt: 7
  memory_bandwidth: 8
  max_ram: 9
  storage_if: 9
  display_if: 9
  camera_media: 8
  linux_driver: 8
  upstream_health: 8
  firmware_dep: 6
  secure_boot: 9
  tpm_se: 9
  virtualization: 9
  usb4: 9
  pcie: 9
  wireless: 7
  modem: 5
  thermal: 6
  battery: 6
  lifecycle: 8
  moq: 6
  docs: 8
  nda: 5
  mfg: 7
  repair: 6
  cost: 5
  lts: 8
  notes: Strong upstream Linux; USB4; discrete modem still needed; higher BOM cost
amd_ryzen_ai_9_hx_370:
  score_sum: 213
  cpu: 9
  gpu: 9
  npu: 9
  perf_per_watt: 8
  memory_bandwidth: 9
  max_ram: 9
  storage_if: 9
  display_if: 9
  camera_media: 8
  linux_driver: 7
  upstream_health: 7
  firmware_dep: 6
  secure_boot: 8
  tpm_se: 8
  virtualization: 9
  usb4: 8
  pcie: 9
  wireless: 7
  modem: 5
  thermal: 6
  battery: 7
  lifecycle: 7
  moq: 5
  docs: 7
  nda: 5
  mfg: 6
  repair: 6
  cost: 4
  lts: 7
  notes: Excellent NPU for local AI; Linux maturity improving; cost/availability risk
rockchip_rk3588s:
  score_sum: 175
  cpu: 6
  gpu: 6
  npu: 5
  perf_per_watt: 8
  memory_bandwidth: 6
  max_ram: 6
  storage_if: 7
  display_if: 7
  camera_media: 7
  linux_driver: 5
  upstream_health: 5
  firmware_dep: 4
  secure_boot: 5
  tpm_se: 4
  virtualization: 4
  usb4: 2
  pcie: 6
  wireless: 5
  modem: 4
  thermal: 7
  battery: 8
  lifecycle: 7
  moq: 8
  docs: 6
  nda: 8
  mfg: 8
  repair: 7
  cost: 9
  lts: 5
  notes: Low cost/equity-friendly; weaker USB4/security/upstream; blob risk
qualcomm_snapdragon_x_elite:
  score_sum: 194
  cpu: 8
  gpu: 8
  npu: 9
  perf_per_watt: 9
  memory_bandwidth: 8
  max_ram: 8
  storage_if: 8
  display_if: 8
  camera_media: 8
  linux_driver: 5
  upstream_health: 4
  firmware_dep: 3
  secure_boot: 8
  tpm_se: 8
  virtualization: 6
  usb4: 7
  pcie: 7
  wireless: 9
  modem: 8
  thermal: 8
  battery: 9
  lifecycle: 7
  moq: 4
  docs: 4
  nda: 2
  mfg: 5
  repair: 5
  cost: 5
  lts: 6
  notes: Great integrated modem path; heavy NDA/blob; Linux still constrained


## Decision
**Selected baseline:** `intel_core_ultra_7_155H` (`Intel Core Ultra 7 155H` class, LPDDR5x, discrete WWAN).

Rationale: best balance of upstream Linux/gunnchOS driver health, USB4 docking, secure boot/TPM path, virtualization, and local NPU without Qualcomm-class NDA lock-in. Equity cost is higher than RK3588 — mitigated by repairability and long support; RK3588 retained as cost-down alternate.

## Frozen measurable specs (engineering baseline)
- CPU: Intel Core Ultra 7 155H (16 cores: 6P+8E+2LP-E) or form-factor-equivalent Ultra 7 H-series with equal-or-better NPU
- GPU: Intel Arc graphics (Xe-LPG) as integrated
- NPU: Intel AI Boost ≥ 10 TOPS (use platform-reported TOPS; do not invent)
- RAM: 32 GB LPDDR5x-7467 dual-channel soldered (serviceability tradeoff documented); dual-source to 16 GB cost-down SKU
- Storage: 1× 2230/2280 NVMe PCIe 4.0 ×4 socketed 512 GB (user-replaceable)
- Display interface: eDP 1.4/1.5 to 14.5" panel
- USB4: 2× USB4 40 Gbps Type-C with DP Alt Mode + PD 3.1 EPR path (silicon must match; no 80 Gbps claim unless controller implements)
- Wi-Fi/BT: Intel Wi-Fi 7 (BE200 class) M.2
- Cellular: M.2 3052 WWAN — Quectel RM520N-GL class 5G-Advanced-capable modem (exact MPN frozen in ADR-FP-005)
- Security: Intel PTT + discrete optional Infineon SLB9672 TPM 2.0 footprint
- Battery: 4S1P or 3S2P Li-ion 60–70 Wh pack with fuel gauge (BQ40Z50 class)

## Alternates
1. Cost-down: Rockchip RK3588S 16 GB + eMMC/UFS — **education SKU only**, reduced USB4/game GPU expectations documented
2. AI-max: AMD Ryzen AI 9 HX 370 — if NPU eval proves material win and Linux stack closes

## Consequences
- Update `device_designs/student_14_5/component_bom.csv` with exact MPNs
- Reject any remaining TBD SoC lines
- Modem/RF still needs ADR-FP-005; panel ADR-FP-006
