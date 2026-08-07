# GATE 1 Physical Capability Inventory

Generated: 2026-08-07T20:48:01Z

- Host: `macOS-26.5.2-arm64-arm-64bit`
- Token: `GATE_1_PHYSICAL_EVIDENCE_PENDING`
- Assumption: Equipment existence is NEVER assumed. PRESENT_CONFIRMED requires observation.

## Command

```bash
python -m gate1.operator.cli inventory
python -m gate1.operator.cli plan
```

## Observed host/toolchain items

| Item | Presence | Label |
|---|---|---|
| macos.host_hardware | PRESENT_CONFIRMED | macOS SPHardwareDataType |
| macos.usb_bus | MISSING | macOS USB device bus |
| macos.ioreg | PRESENT_CONFIRMED | IOKit registry probe |
| macos.power | PRESENT_CONFIRMED | Power management probe |
| macos.networksetup | PRESENT_CONFIRMED | Network setup probe |
| macos.ifconfig | PRESENT_CONFIRMED | Network interfaces |
| usb.ioreg | MISSING | IOUSB registry |
| android.adb | TOOLCHAIN_MISSING | Android Debug Bridge |

- Summary: {"capabilities_present_confirmed": 0, "missing": 2, "observed_count": 8, "present_confirmed": 5, "toolchain_missing": 1}

## Gate 1 capabilities (never auto-confirmed from host probes alone)

| Capability | Workstream | Presence | Blocker |
|---|---|---|---|
| representative_boot_hardware | boot | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |
| ring_prototype | ring-auth | MISSING_ASSUMED | REQUIRES_PHYSICAL_PROTOTYPE |
| dock_station | dock | MISSING_ASSUMED | REQUIRES_PHYSICAL_PROTOTYPE |
| on_device_ai_runtime_target | ai-runtime | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |
| game_target_device | games | MISSING_ASSUMED | REQUIRES_LOCAL_HARDWARE |

## High-level findings
- Host inventory tooling is available (system_profiler/ioreg/pmset/networksetup/ifconfig).
- USB bus observation did not confirm Gate 1 prototypes.
- `adb` toolchain missing on this host (`TOOLCHAIN_MISSING`).
- All Gate 1 physical capabilities remain `MISSING_ASSUMED` — **not** physical closure.
