# RING Prototype Assembly and Bring-Up

**Status:** `RING_FABRICATION_READY` procedure documented · `RING_PHYSICAL_PROTOTYPE_BLOCKED` execution  
**Physical ring claimed:** `false`  
**Do not mark ACCEPTED from this document.**

This is the operator procedure for a future first article. Every checklist item below is **blocked** until MISSING items are resolved: gerbers, routed PCB, MCU firmware binary, physical ring (or explicitly labeled bench mule — still not a ring).

---

## 0. Preconditions (all required)

| # | Precondition | Current |
|---|---|---|
| P1 | Candidate BOM reviewed (`RING_PROTOTYPE_BOM.csv`) | Research only — no purchases claimed |
| P2 | Schematic peer review + ERC | **MISSING** (ring) |
| P3 | Routed PCB + DRC clean | **MISSING** |
| P4 | Fab package (Gerbers, drill, pick-place, assembly drawing) | **MISSING** |
| P5 | Assembled first article or labeled bench mule on hand | **MISSING** / blocked |
| P6 | MCU firmware binary implementing authenticated codec (or mule equivalent) | **MISSING** |
| P7 | Host software: protocol + edge-io harness + device-os adapter | Available (software) |

If any of P2–P6 fail, stop. Record `RING_PHYSICAL_PROTOTYPE_BLOCKED`. Do not invent evidence.

---

## 1. Assembly (when PCB + parts exist)

1. ESD-safe station; verify BOM line IDs against pick-place.
2. Place MCU, IMU, PMIC/protection, haptic (if present), passives per assembly drawing.
3. Visual / AOI for tombstones and polarity on battery connector.
4. **Do not connect LiPo until protection path verified** (continuity on pack sense / charge path).
5. Photograph first article (serial / lot) for physical evidence bundle — only if board is real.

Bench mule alternate (not a ring):

1. Wire nRF52840 DK + BMI270 breakout + USB power.
2. Label inventory item `RING_MULE_BENCH` — never upgrade claim to `ring_prototype` without form-factor hardware.

---

## 2. Flashing

1. Connect SWD / USB DFU per SoC module guidance.
2. Flash **only** a built firmware artifact with recorded hash:

```bash
# Placeholder — replace with real image path when binary exists
# sha256sum build/ring_auth_fw.bin
# nrfjprog --program build/ring_auth_fw.bin --chiperase --verify --reset
```

3. Record: image path, SHA-256, tool version, chip ID, UTC time.
4. If no binary exists → stop with `MCU_FIRMWARE_BINARY_MISSING`.

Firmware must implement (or wrap) authenticated ring protocol properties: pairing SM, challenge-response HMAC, monotonic seq, session MAC, freshness, revocation honor. Unauthenticated Edge-IO SENSOR notifies alone are **insufficient** for G1-C2 physical PASS.

---

## 3. Electrical smoke / BLE bring-up

| Step | Action | Pass criterion |
|---|---|---|
| E1 | Apply power via protected path | No smoke / thermal runaway; rails in spec |
| E2 | USB/SWD enumerates | Chip ID matches expected |
| E3 | BLE advertises | Visible in nRF Connect / Web Bluetooth within 60 s (research target) |
| E4 | IMU samples | Rates match firmware config; axes mapped |
| E5 | Haptic (optional) | Host write produces detectable buzz |

---

## 4. Authenticated protocol acceptance (software hosts)

On a development Mac/Linux host with sibling repos checked out:

```bash
# Protocol unit tests (software) — already the Gate 1 software path
cd /Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-hardware-industrial-design/ring_input
PYTHONPATH=python pytest -q tests

# Measurement harness
cd /Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/edge-io-measurement-node
pytest -q tests/test_ring_input_harness.py

# OS adapter
cd /Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-device-os
pytest -q tests/test_ring_input_adapter.py
```

Physical session (only when ring/mule `PRESENT_CONFIRMED`):

```bash
cd /Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit
python -m gate1.operator.cli inventory
python -m gate1.operator.cli start-session --workstream ring-auth
# Capture authenticated frame with anti-replay nonce + payload digest
python -m gate1.operator.cli finalize-session --session <session_id>
python -m gate1.operator.cli validate-bundle --bundle <bundle_path>
# ACCEPT only with Edmund decision record — never auto
```

### Physical accept cases (when hardware exists)

| Case | Expected |
|---|---|
| Valid paired session event | Accept → OS adapter maps input |
| Bad signature / replay / revoked / wrong target | Reject + audit (no raw IMU persist) |
| Auth failure / link loss | Fallback keyboard/touch — never silent accept |

---

## 5. Safety stops

- Abort if protection IC missing or pack voltage out of range.
- Abort wear tests without thermal / charge supervision.
- Do not claim FCC/CE or UN38.3 completion from this checklist alone.

---

## 6. Outcome tokens

| Outcome | Token |
|---|---|
| Docs + procedure ready; no hardware | `RING_FABRICATION_READY` + `RING_PHYSICAL_PROTOTYPE_BLOCKED` |
| Bench mule only | `RING_MULE_BENCH` (optional) — still not physical ring PASS |
| Physical authenticated evidence accepted by Edmund | Requires `accept-bundle` + decision record — **not** set by this doc |

**Current freeze:** `RING_PHYSICAL_PROTOTYPE_BLOCKED` · **NOT ACCEPTED**
