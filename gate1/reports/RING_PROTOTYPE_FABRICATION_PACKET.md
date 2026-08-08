# RING Prototype Fabrication Packet (Gate 1 / G1-C2)

**Status:** `RING_FABRICATION_READY` · `RING_PHYSICAL_PROTOTYPE_BLOCKED`  
**Physical ring claimed:** `false`  
**Evidence class for protocol path:** `SOFTWARE_SIMULATED` (upstream)  
**Generated:** 2026-08-07T21:58:36Z  
**Workspace:** `gunnchos-7gc-ai-ran-field-kit` branch `cursor/gate1-max-automation-closure`

This document packages a **candidate** first-article ring prototype path from existing research. It does **not** assert that a PCB was fabbed, parts were purchased, firmware was flashed, or a wearable ring exists.

---

## 1. Purpose and claim boundary

| Claim allowed | Claim forbidden |
|---|---|
| Research candidates for MCU / IMU / BLE / power / haptic | Purchased inventory or landed cost |
| Mapping firmware duties to authenticated ring protocol | Physical authenticated IMU frames |
| Bring-up procedure ready for when hardware arrives | Completed EVT / DVT / FCC |
| Fabrication packet complete enough to quote / layout | Gerbers exist / board routed |

### Explicitly MISSING

1. **Gerbers** (and drill / pick-place / assembly drawings for ring)
2. **Routed PCB** (no ring layout EVT)
3. **MCU firmware binary** for the ring target
4. **Physical ring** (any form factor)

---

## 2. Electrical architecture (research target)

Derived from wearables / Edge-IO research specs and anime-aggressors ring target BOM (research stubs).

```text
  [LiPo 50–100 mAh pouch] ──► [Charger / protection IC] ──► [3V3 rail]
                                      │
                                      ▼
                              [nRF52-class SoC]
                               │        │        │
                          BLE 5.x    I2C/SPI   GPIO/PWM
                               │        │        │
                          Host hub   [BMI270]  [DRV2605L → LRA]
                                     6-axis      haptic
```

| Block | Role | Notes |
|---|---|---|
| MCU + BLE SoC | App + radio + crypto primitives for pairing / HMAC | Prefer integrated BLE SoC over discrete BLE radio for ring volume |
| IMU | Gesture / pointer motion source | Placement vs finger axis is a mechanical risk (research TBD) |
| Haptic | Host→device feedback (optional for Gate 1 auth path) | Output-only; not required for MAC verify |
| PMIC / charger | Charge + undervoltage / overcurrent protection | Body-worn → battery safety review before any powered wear |
| Antenna | Chip / PCB trace BLE | Keep-out vs battery and finger tissue (RF plan TBD) |

Cross-ref research stack label: `wearables_arena_set` → *Low-power MCU/SoC, BLE/UWB class, IMU, haptic driver, BMS* (`gunnchos-hardware-industrial-design/component_selection/RECOMMENDED_COMPONENT_STACKS.md`) — **simulated / concept-complete**, not DVT-validated.

Primary workload targets (Edge-IO wearables research spec): IMU sensing, haptic actuation, BLE body-area link; 15–60 minute sessions; event-to-feedback latency budgets documented as research targets (not measured on ring hardware).

---

## 3. MCU / IMU / BLE candidates (research)

Sources: anime-aggressors `hardware/ring/bom/edgeio-ring-target-bom.csv`, `hardware/ring/bom.csv`, `hardware/ring/REQUIREMENTS.md` (RG-E-*), and wearables arena component stacks.

| Domain | Preferred research candidate | Alternate / note | Status column |
|---|---|---|---|
| MCU + BLE | Nordic **nRF52840** (WLCSP or module) | Size-optimized nRF52/nRF54 variant TBD | `RESEARCH_CANDIDATE` |
| IMU | Bosch **BMI270** 6-axis | Other 6-axis (LSM6* class) only after placement study | `RESEARCH_CANDIDATE` |
| Haptic driver | TI **DRV2605L** + LRA/ERM | Optional for auth-only bring-up | `RESEARCH_CANDIDATE` |
| Battery | LiPo **50–100 mAh** curved pouch | Coin-cell path exists in wearables energy notes; pouch preferred for recharge | `TBD_QUOTE` |
| Charger / protection | TBD PMIC + protection IC | Must include protection before wear | `TBD_QUOTE` |
| Enclosure | Ring band / shell TBD | Mechanical after wristband mule lessons (anime-aggressors sequencing) | `RESEARCH_CANDIDATE` |

**Honesty:** anime-aggressors ring REQUIREMENTS state Gate R0 planning only — *no KiCad, no Gerbers, no EVT* for the ring form factor. Wearables arena electrical tree includes schematic stubs for the *arena set*, not a completed ring fab package.

Dev-board mule path (allowed before miniaturized ring): nRF52840 DK + BMI270 breakout + wired power — still **not** a physical ring prototype; label as `RING_MULE_BENCH` if used later.

---

## 4. Power

| Item | Research posture |
|---|---|
| Energy class | Coin-cell **or** small LiPo; extreme efficiency; thermal limits for body-worn (edge-io wearables research spec) |
| Candidate capacity | 50–100 mAh LiPo pouch (anime-aggressors ring BOM) |
| Wearables arena power budget CSV | `active/idle/sleep` mW rows exist as **research stubs** for arena set — do not treat as measured ring draw |
| Safety | Protection IC required; UN38.3 path documented under wearables power_battery docs — **not executed** for a ring cell |
| Charge | USB-C / pogo / cradle TBD — enclosure ID alignment required before layout |

No battery has been ordered or charged under this packet.

---

## 5. PCB approach (fabrication-ready *plan*, not fabbed board)

| Stage | Intent | Current state |
|---|---|---|
| 0. Protocol software | Authenticated events over simulated stream | Available (`AUTHENTICATED_INPUT_PROTOCOL_PASS`) |
| 1. Bench mule | DK + breakout; validate BLE + IMU binary + auth MAC | Not executed in this workspace |
| 2. Schematic | Capture netlist for ring SoC + IMU + PMIC + haptic | **MISSING** for ring (arena schematic stubs ≠ ring) |
| 3. Layout | Flex or rigid-flex ring PCB; antenna keep-outs | **MISSING** — no routed PCB |
| 4. Fab outputs | Gerbers, drill, pick-place, assembly drawing | **MISSING** |
| 5. Assembly / bring-up | See assembly doc | **BLOCKED** (`RING_PHYSICAL_PROTOTYPE_BLOCKED`) |

**Do not invent Gerbers.** When layout exists, store under a dedicated fab export path and link from `gate1/ring_fabrication/references.md` — never claim fab without files + PO evidence.

Recommended process after owner approval to spend:

1. Freeze schematic revision + BOM quote statuses (`TBD_QUOTE` → quoted).
2. Peer review (ERC/DRC).
3. Generate fab package; archive hashes in physical evidence session.
4. Assemble first article; run `RING_PROTOTYPE_ASSEMBLY_AND_BRINGUP.md`.

---

## 6. Firmware target mapping → authenticated ring protocol

Normative protocol:  
`gunnchos-hardware-industrial-design/ring_input/docs/AUTHENTICATED_RING_INPUT_PROTOCOL.md`

Firmware on the ring MCU must eventually implement (or securely forward) the following; today only **Python reference + fixtures** exist:

| Protocol property | Firmware / device duty | Host / OS duty |
|---|---|---|
| Device identity | Store `device_id` + long-term key material in protected region | Trust store / pairing record |
| Pairing SM | `DISCOVER → CHALLENGE → VERIFY → CONFIRM → PAIRED` | Drive ceremony; persist pairing offline |
| Challenge-response | HMAC over challenge + identities | Issue `challenge_nonce`; verify |
| Ephemeral session | Derive session key; TTL expire | Session cache |
| Monotonic `seq` | Increment by 1 per event | Reject gaps / replays |
| Integrity `mac` | HMAC-SHA256 over canonical payload | Verify before accept |
| Source/target binding | Embed `source_device_id` / `target_device_id` | Reject wrong target |
| Freshness `ts_ms` | Clock / sync policy | `max_skew_ms` window |
| Confidence | Emit `confidence`; gate destructive locally if needed | Enforce `min_confidence` |
| Calibration / surface | Carry `calibration_id` / `surface_id` | Match active calibration session |
| Revocation | Honor revoke command / refuse if revoked | Revocation registry |
| Audit | No persistent raw IMU by default | Structured audit without raw motion |
| Safe fallback | On link loss, stop privileged emits | Keyboard/touch fallback — **never silent accept** |

### Transport mapping note

anime-aggressors `firmware/ring/PROTOCOL.md` documents a **BLE notify binary** (SENSOR / GESTURE / HAPTIC / INFO) for Edge-IO. Gate 1 authenticated protocol is a **higher-layer** signed event model. Fabrication-ready firmware plan:

1. BLE transport carries authenticated event frames (or gesture notifies wrapped with MAC + seq + session).
2. Do not ship unauthenticated IMU notifies as Gate 1 physical PASS evidence.
3. MCU firmware binary that implements the authenticated codec is **MISSING**.

Host-side already available (software):

- Protocol encode/decode: `gunnchos-hardware-industrial-design/ring_input/python/authenticated_ring_input/`
- Measurement: `edge-io-measurement-node/src/edge_io_node/ring_input_harness/`
- OS adapter + fallback: `gunnchos-device-os/ring_input/`

---

## 7. Enclosure approach

| Aspect | Research posture |
|---|---|
| Form | Finger ring / band after wristband mule lessons (anime-aggressors sequencing policy) |
| Mechanical research | Wearables arena `mechanical/wearables_arena_set/` (dimensions / tolerance stubs — concept) |
| Antenna | Keep-out vs battery and tissue (`rf_wireless/wearables_arena_set/antenna_zone.md`) |
| Comfort / thermal | Body-worn thermal limits; no skin-contact hot spots from charging |
| Repair | Prefer serviceable battery path only if volume allows; otherwise sealed EVT with safety first |

No enclosure has been printed or molded under this packet.

---

## 8. Bring-up (summary)

Full procedure: [RING_PROTOTYPE_ASSEMBLY_AND_BRINGUP.md](RING_PROTOTYPE_ASSEMBLY_AND_BRINGUP.md).

Blocked gates until physical hardware + firmware binary exist:

1. Power-on without smoke  
2. BLE advertise + authenticated pairing  
3. Signed event accept path via edge-io harness → device-os adapter  
4. Negative tests (replay, bad MAC, revoked) on **physical** frames  
5. Edmund `accept-bundle` with decision record  

---

## 9. Safety

| Topic | Requirement before wear / powered demo |
|---|---|
| Li-ion | Protection IC; charge supervision; no unattended charge in soft goods |
| Thermal | Skin-contact temperature limits; abort on thermal fault |
| RF | Follow pre-scan plan before any “worn for hours” claim; FCC/CE not claimed |
| Privacy | No persistent raw motion in audit logs (protocol default) |
| Ethics | Human-participant sensing may need institutional review (wearables research spec) |
| Software safety | Auth failure → OS fallback input; never silent accept |

Battery safety planning docs exist under wearables `power_battery/wearables_arena_set/` — planning only.

---

## 10. Status freeze for this packet

```text
RING_FABRICATION_READY
RING_PHYSICAL_PROTOTYPE_BLOCKED
MISSING: gerbers, routed PCB, MCU firmware binary, physical ring
NOT ACCEPTED
```

Next physical actions require human acquisition (parts quote / mule board / fab PO) and are outside automated closure.
