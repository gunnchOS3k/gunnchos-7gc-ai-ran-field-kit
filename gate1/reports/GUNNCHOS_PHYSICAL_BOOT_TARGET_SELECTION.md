# gunnchOS Physical Boot Target Selection

**Status:** `GUNNCHOS_PHYSICAL_BOOT_BLOCKED_NO_TARGET`  
**Physical boot claimed:** `false`  
**Generated:** 2026-08-07T21:58:36Z  
**Criterion:** G1-C1

This note freezes **preferred** physical boot targets from device-os / hardware research. It does not claim any target is present on the operator host.

---

## 1. Preferred physical boot targets (priority order)

Aligned with:

- Field-kit `program/decisions/DR-0002-DEVICE-ROLE-BASELINE.md`
- device-os `boot_readiness/BOOT_READINESS_REQUIREMENTS.md` (per-class priority)
- hardware `component_selection/RECOMMENDED_COMPONENT_STACKS.md` + device-quartet research specs

| Priority | Target | Role | Architecture requirements (research) |
|---|---|---|---|
| 1 | **Student 14.5** | Primary full-session learning/work platform | x86-64 mobile APU class; 16–32 GB RAM; NVMe 512GB–1TB; Wi-Fi 6E/7; USB-C PD + DP Alt Mode; TPM 2.0; school-day battery / ~15W thermal envelope (research) |
| 2 | **DS-XL Coder** | Dual-screen build-learning device | Efficient x86 **or** ARM module; 8–16 GB RAM; 256–512 GB storage; dual ~7in touch; USB-C deploy path |
| 3 | **Handheld Hybrid** | Mobile/dockable compute (not entertainment-only) | x86-64 handheld APU; 16 GB RAM; NVMe 512GB+; microSD; 7–8in 1080p; Hall sticks; IMU; active cooling; dock/TV path |

Wearables / Edge-IO rings are **embodied input**, not the gunnchOS full-session boot target (DR-0002).

Hardware existence is **not** claimed by role freeze or this selection doc.

---

## 2. Why Mac is NOT a gunnchOS boot target

| Reason | Detail |
|---|---|
| Product family | Frozen roles are Student 14.5 / DS-XL / Handheld Hybrid / Edge-IO rings — not Apple Silicon Macs |
| OS path | Boot/demo path documents Windows 11 base for Student 14.5 / Handheld EVT-alpha (`docs/BOOT_AND_DEMO_PATH.md`); recovery / secure-boot contracts target those device classes |
| Evidence class | macOS host probes prove **operator tooling**, not `PHYSICAL_BOOT` of gunnchOS |
| Boot matrix | `host-native` probe on developer host is explicitly **N/A (not a device boot)** in `docs/gate1/BOOT_TARGET_MATRIX.md` |

A Mac may:

- Run software boot probes / pytest (`GUNNCHOS_BOOT_SOFTWARE_PATH_PASS` class work)
- Host `adb` / inventory / evidence CLI
- Cross-compile or serve images

A Mac must **not** be recorded as `representative_boot_hardware` = `PRESENT_CONFIRMED` for G1-C1 physical PASS.

---

## 3. Architecture requirements (acceptance-facing)

For T1 hardware boot readiness (device-os BR-001…BR-012 summary):

1. Power-on to bootloader  
2. Bootloader loads OS image  
3. SKU detection or user-confirmed once  
4. Primary display at profile resolution  
5. Primary input functional  
6. Storage ≥ profile minimum  
7. Battery fuel gauge readable (if battery SKU)  
8. Thermal sensors readable (if active-cooling SKU)  
9. Safe mode reachable  
10. USB recovery image boots  
11. First-run binding completes  
12. Unsupported mode falls back without brick  

Simulated T0 profile checks are **not** physical boot evidence.

---

## 4. Flashing path outline (when a real target exists)

```text
1. Inventory → require PRESENT_CONFIRMED for representative_boot_hardware
2. Select image channel for SKU (Student 14.5 / DS-XL / Handheld)
3. Write recovery / install media (USB) per device-os recovery contracts
4. Enter bootloader / recovery on device (SKU-specific keys / USB)
5. Flash or install image; record image SHA-256 + tool versions
6. First boot → capture identity, boot duration, services, storage, display/input, network
7. python -m gunnchos_device_os.boot --physical-capture
   (or scripts/gunnchos_physical_boot_capture.py)
8. field-kit: start-session --workstream boot → finalize → validate-bundle
9. Edmund accept-bundle with decision record only
```

Toolchain notes:

- Offline software path: pytest + sample manifest — available  
- Docker compose under `os_build/` — **optional**; deferred on this host (see toolchain report)  
- QEMU full-system smoke — `BLOCKED_TOOLCHAIN` in device-os docs; not claimed here  

---

## 5. Current host freeze

| Item | State |
|---|---|
| Preferred targets documented | Yes (this file) |
| Physical candidate observed | No |
| Mac used as boot target | **Forbidden** |
| Token | **`GUNNCHOS_PHYSICAL_BOOT_BLOCKED_NO_TARGET`** |

Related: `GATE_1_PHYSICAL_EVIDENCE_PENDING` · G1-C1 not ACCEPTED.
