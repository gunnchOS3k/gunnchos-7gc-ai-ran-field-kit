# EVT Physical Test Book — Cont IX (procedures before boards exist)

Updated: 2026-08-10T01:51:42Z
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

## 7. Frontier feature companion stubs (Phase XIV)
PHYSICAL_PENDING — procedures only; no physical execution under PHYSICAL_EXECUTION_FREEZE.

| Feature | EVT assertions (PHYSICAL_PENDING) | Limits |
|---------|-----------------------------------|--------|
| Compositor | frame pacing (ms), display hotplug reconnect time | TARGET_TO_CONFIRM |
| Local AI | TTFT (ms), tokens/s, power (W), skin thermals (°C) | TARGET_TO_CONFIRM |
| gunnchPlay | FPS, frame time p95, resume latency | TARGET_TO_CONFIRM |
| Remote Play | end-to-end latency, video quality score, packet loss | TARGET_TO_CONFIRM |
| SpatialInput | pose error, drift, end-to-end latency | TARGET_TO_CONFIRM |
| Continuity | network handoff latency, session resume integrity | TARGET_TO_CONFIRM |
| Fabric | capability transport latency, auth/lease revoke | TARGET_TO_CONFIRM |
| Voice | mic/speaker round-trip latency, noise floor | TARGET_TO_CONFIRM |

Do not move these into the digital defect backlog. Digital PASS ≠ physical PASS.

**Product focus (first_party_dock):** Primary: compositor display hotplug / dock SI, Fabric transport, Continuity USB/Ethernet path. Secondary: Remote Play uplink.

