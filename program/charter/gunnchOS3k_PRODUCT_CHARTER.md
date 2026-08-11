# gunnchOS3k Product Charter

**Canonical home:** `gunnchos-7gc-ai-ran-field-kit` (`program/charter/`)  
**Machine-readable twin:** `gunnchOS3k_PRODUCT_CHARTER.yaml`  
**Status:** definition content complete *candidate* — `PRODUCT_CHARTER_DEFINITION_COMPLETE` becomes true only when Edmund merges the final charter PR  
**Supersedes as current authority:** earlier Gate-0 ingest at `program/charters/GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md` (retained as historical source ingest)

---

## 1. Mission

gunnchOS3k is a carrier-grade-targeted equitable compute ecosystem built around affordable first-party computing devices, gunnchOS, local-first gunnchAI3k intelligence, spatial Ring input, education, creation, work, gaming, and resilient connectivity.

Connectivity posture: **5G-Advanced and NTN-capable architecture where supported, IMT-2030-aligned, software-defined, and engineered for migration to standardized 6G as standards and commercial ecosystems mature.**

### Claim boundary (non-negotiable)

- Do **not** claim current standardized commercial 6G, final IMT-2030 compliance, carrier approval, or certification unless independently evidenced.
- Do **not** claim frontier AI parity until benchmarked.
- Do **not** infer NTN capability from the presence of an RM520N-GL modem alone.
- “Carrier-grade-targeted” means reliability, security, fleet ops, safe updates, multi-bearer connectivity, and evidence discipline — not a conferred carrier certificate.
- Cursor opens **DRAFT** PRs only; Edmund merges. No RFQ send, fab, purchase, or production release from this charter alone.

---

## 2. First-party product family

Exactly five physical products:

| Product | Role | Primary purpose |
|---|---|---|
| Student 14.5 | Sustained learning/work | Full-session academic, research, creation, and desktop-class use |
| Handheld Hybrid | Mobile/docked compute | Portable learning, field work, play, and docked desktop expansion |
| DS-XL Coder | Learn/build/test/deploy-local | Dual-screen creation, debugging, and hands-on build education |
| Edge I/O Rings | Embodied low-latency input | Authenticated spatial/surface input to intended apps/devices |
| First-party Dock | Continuity / desktop expansion | Displays, power, Ethernet, USB, and session continuity |

Gaming must not erase Student/work/education purpose. No first-party device is entertainment-only.

### 2.1 Student 14.5

- **User role:** student, educator, knowledge worker, creator.
- **Use cases:** assignments, research, coding, creative production, communication, docked multi-display, full game experiences.
- **Hardware architecture source:** `gunnchos-hardware-industrial-design` (`device_designs/student_14_5/`).
- **gunnchOS role:** primary desktop-class shell, continuity host, local AI runtime, secure update/recovery.
- **gunnchAI role:** tutoring, coding help, research/citations, accessibility, device help (local-first).
- **Inputs:** keyboard, touch, Rings, controller, voice, dock peripherals.
- **Displays:** built-in 14.5-class panel + external via dock/ports.
- **Docking:** First-party Dock for expansion and continuity.
- **Connectivity:** Wi-Fi, Ethernet (dock), Bluetooth/UWB where accepted, RM520N-GL 5G NR Sub-6 baseline where SKU includes it; 5G-Advanced software architecture; NTN via abstraction/simulation/migration paths — never inferred from modem SKU alone.
- **Golden Journeys:** 1, 2, 3, 4, 8, 9, 10 (primary); others as applicable.
- **Current evidence level:** digital design/integration evidence in hardware + device-os; physical EVT/HIL **PHYSICAL_PENDING**.
- **Remaining gates:** EVT calibration, battery/thermal/RF, human preference (E6), certification/carrier (E7).

### 2.2 Handheld Hybrid

- **User role:** mobile learner, field researcher, gamer, docked worker.
- **Use cases:** portable learning, media, field notes, handheld play → dock → work → undock.
- **Hardware architecture source:** `gunnchos-hardware-industrial-design` (`device_designs/handheld/`).
- **gunnchOS role:** adaptive UI, dock manager, session continuity, power/thermal profiles.
- **gunnchAI role:** local help, tutoring packs, connectivity diagnosis, accessibility.
- **Inputs:** touch, buttons, Rings, dock keyboard/mouse, controller.
- **Displays:** handheld panel; docked external displays.
- **Docking:** First-party Dock; continuity of apps, identity, saves, layout, audio.
- **Connectivity:** same family posture as Student; handheld power/antenna constraints apply.
- **Golden Journeys:** 5 (primary), 1–4, 7–10 as applicable.
- **Current evidence level:** digital/sim + design; physical **PHYSICAL_PENDING**.
- **Remaining gates:** physical continuity SI, RF, thermal, human quality.

### 2.3 DS-XL Coder

- **User role:** learner-builder, developer, educator lab lead.
- **Use cases:** IDE + docs/logs, dual-screen coding, local build-test-deploy, game/tool authoring.
- **Hardware architecture source:** `gunnchos-hardware-industrial-design` (`device_designs/ds_xl/`).
- **gunnchOS role:** dual-output compositor, focus/layout restoration, developer mode boundaries.
- **gunnchAI role:** coding assistance, research help, lab coaching (local-first).
- **Inputs:** keyboards, touch, Rings, controllers.
- **Displays:** two functional screens (not decorative); external via dock where supported.
- **Docking:** supported for expansion; dual-screen identity remains primary.
- **Connectivity:** family posture; lab Ethernet preferred for sustained builds.
- **Golden Journeys:** 6 (primary), 3, 8.
- **Current evidence level:** Device Lab DRM/enumeration digital; dual-screen UX depth under WP-011R scrutiny; physical **PHYSICAL_PENDING**.
- **Remaining gates:** two-display visual/application proof on target hardware; EVT.

### 2.4 Edge I/O Rings

- **User role:** any authenticated user needing embodied or surface input.
- **Use cases:** document/browser/game control when traditional I/O is unavailable or secondary; accessibility.
- **Hardware architecture source:** `gunnchos-hardware-industrial-design` + ring sensing stack; gesture research lineage includes EdgeGesture work.
- **gunnchOS role:** RingService → SpatialInputService → confidence/target gate → guest/OS input injection.
- **gunnchAI role:** optional intent assistance; must not silently approve destructive actions.
- **Inputs:** multi-modal sensing (IMU alone is **not** absolute spatial registration).
- **Displays:** feedback on target device (visual/haptic/audio).
- **Docking:** N/A as dock product; pairs to devices.
- **Connectivity:** secure local link (BT/UWB/etc. as accepted); offline input required.
- **Golden Journeys:** 7 (primary).
- **Current evidence level:** digital pipeline partial; physical spatial accuracy **PHYSICAL_PENDING**.
- **Remaining gates:** Ring-to-real-app physical proof, calibration, anti-spoof, human comfort (E6).

**Plain-English Rings intent:** Rings allow authenticated user input to be inferred from interaction with nearby surfaces/devices and routed to the intended application/device, with spatial/target confidence and safe rejection.

### 2.5 First-party Dock

- **User role:** any docked Student/Handheld/DS-XL user.
- **Use cases:** office workflow, displays, Ethernet, charging, continuity.
- **Hardware architecture source:** `gunnchos-hardware-industrial-design` (`device_designs/dock/`); ADR-FP-006.
- **gunnchOS role:** `dock_manager`, display/audio routing, safe undock.
- **gunnchAI role:** optional device help during dock transitions.
- **Inputs:** passes through USB/HID; Rings remain usable.
- **Displays:** HDMI/DP downstream per silicon class.
- **Docking:** *is* the dock.
- **Connectivity:** RJ45 Ethernet + upstream device radios.
- **Golden Journeys:** 4, 5.
- **Current evidence level:** design baseline; USB-IF/logo and physical SI **EXTERNAL_PENDING** / **PHYSICAL_PENDING**.
- **Remaining gates:** silicon freeze for EVT, electrical bring-up, certification marks.

---

## 3. Software / platform family

| Component | Purpose | Owner / primary repos |
|---|---|---|
| gunnchOS | Common OS across first-party devices | `gunnchos-device-os` |
| gunnchAI3k | Local-first intelligent system layer (not chatbot-only) | `gunnchAI3k` |
| gunnchDevice Lab | Virtual device/ecosystem verification before/alongside physical | `gunnchos-device-os` (lab) + field-kit aggregation |
| WAIKE | Wireless + AI kinesthetic education / community ops | `waike-research-ops` |
| Creator / Coder Studio | Build, package, install pathways | device-os + app tooling |
| Device Management | Fleet, identity, revoke, MDM-shaped controls | device-os |
| Continuity / fabric | Cross-device session and user-owned sync | device-os |
| Connectivity orchestrator | Multi-bearer policy, degrade/offline | device-os + `ntn-resilience-sim` + research repos |
| Security / update / recovery | Boot, signing, OTA, rollback, recovery | device-os + hardware RoT |
| Anime Aggressors | Platform fighter lab/product game | `anime-aggressors` |
| Pedestrian Pursuit | Foot-racing arcade | `pedestrian-pursuit` |
| Archive of Life | Scientific life-record exploration game | `archive-of-life-artifact-world` |
| Beat Link | Rhythm / party participation | `beatlink-party` |

Control plane / charter: **this repo** (`gunnchos-7gc-ai-ran-field-kit`).  
Public navigation: **`gunnchos-research-portal`** (Ecosystem Portal).  
Profile front door: **`gunnchOS3k/gunnchOS3k`**.

---

## 4. Sixteen system layers

| # | Layer | Owner repo(s) | Interfaces | Definition of done | Current state | Downstream deps |
|---|---|---|---|---|---|---|
| 1 | Industrial design | hardware-industrial-design | CAD, ergonomics, thermal envelopes | DFM-ready enclosure set | DESIGNED / digital | electrical, mfg |
| 2 | Electrical hardware | hardware-industrial-design | schematics, BOM, antennas | EVT board bring-up | DESIGNED | firmware, cert |
| 3 | Firmware | hardware + device-os | boot, BMC/EC, radio FW, ring FW | signed boot chain on target | IMPLEMENTED (partial digital) | OS |
| 4 | gunnchOS | device-os | HAL, services, shell, packages | boots + services on SKU | DIGITALLY progressing; physical pending | apps, AI, games |
| 5 | gunnchAI3k | gunnchAI3k | local runtime, routing, governance | local essential features offline | IMPLEMENTED (no frontier-parity claim) | apps, tutoring |
| 6 | Connectivity | device-os, ntn-resilience-sim, spectrumx, 7gc | bearers, policy, NTN abstraction | honest multi-bearer + offline | architecture + sim; NTN not from RM520N-GL | campus, ops |
| 7 | Input ecosystem | device-os, rings, EdgeGesture lineage | Ring/touch/HID/voice | confidence-gated real input | digital partial | apps, games |
| 8 | Applications | device-os app layer + studios | packaging, sandbox | installable real apps | partial | continuity |
| 9 | Games | four game repos | saves, input, performance | production runtime loops | digital runtimes vary; Device Lab bar rising | AI lab, rings |
| 10 | Cloud/edge | device-os + ops services | identity, sync, matchmaking | user-owned, revocable | partial | support |
| 11 | Security operations | device-os + field-kit policy | SBOM, disclosure, IR | exercised playbooks | digital policy; external pentest pending | cert, deploy |
| 12 | Manufacturing | hardware + field-kit mfg docs | RFQ packets, traceability | DFM + supplier path | prep only — no RFQ send in Cycle 3A | PVT |
| 13 | Certification | hardware + compliance track | radio/safety/carrier | lab reports | STANDARD_PENDING / EXTERNAL_PENDING | release |
| 14 | Deployment | WAIKE + 7GC + ops | logistics, activation | pilot playbooks | EXTERNAL/HUMAN pending | support |
| 15 | Support | docs + portal + ops | repair, warranty, recovery | documented procedures | DIGITAL draft | operated |
| 16 | Evidence | field-kit + owner repos | E0–E8 / D0–D8 records | claim ≤ evidence | active control plane | all claims |

---

## 5. Product principles

1. Affordable / equitable access  
2. Education + work + creation + gaming balance  
3. Local-first privacy  
4. User-owned context / continuity  
5. Repairability / serviceability  
6. Accessibility  
7. Security by default  
8. Software-defined connectivity  
9. Standards honesty  
10. Evidence before claims  
11. No toy demo as product proof  
12. No fixture/mock as final runtime  
13. Real-user quality  
14. Graceful offline behavior  

---

## 6. Device balance

- **Student 14.5** → sustained learning/work  
- **Handheld** → mobile/docked compute  
- **DS-XL** → learn/build/test/deploy-local  
- **Rings** → embodied low-latency input  
- **Dock** → continuity / desktop expansion  

---

## 7. AI intent (gunnchAI3k)

Not merely a chatbot. Scope includes tutoring, coding, research/citations, device help, accessibility, translation, game coaching, connectivity diagnosis, scientific attribution, agents/tools, memory/projects, local/cloud routing, and privacy/governance.

Essential features must work offline. Cloud may enhance; it must not be the only path to basic operation. No frontier-parity claim without benchmarks.

---

## 8. Connectivity intent

Covered paths: Wi-Fi, Ethernet, Bluetooth/UWB where accepted, RM520N-GL 5G NR Sub-6 baseline, 5G-Advanced software architecture, multi-bearer policy, NTN abstraction/simulation/migration, and future standardized-6G migration.

**Never infer NTN from RM520N-GL.**

---

## 9. Completion vocabulary

### Status words

TARGET → DESIGNED → IMPLEMENTED → INTEGRATED → DIGITALLY_VALIDATED → COMPETITIVELY_VALIDATED → PHYSICAL_PENDING → PHYSICALLY_VALIDATED → EXTERNAL_PENDING → EXTERNALLY_VALIDATED → CERTIFIED → DEPLOYED → OPERATED.

### Evidence levels (E0–E8)

| Level | Meaning |
|---|---|
| E0 | Requirement/design only |
| E1 | Implementation exists |
| E2 | Component/unit test |
| E3 | Integrated automated execution |
| E4 | Independent digital verification |
| E5 | Actual target-hardware validation |
| E6 | Human/user validation |
| E7 | External lab/vendor/carrier validation |
| E8 | Production/field evidence |

### Depth ladder (D0–D8)

| Depth | Meaning |
|---|---|
| D0 | Requirement |
| D1 | Interface/schema |
| D2 | Implementation |
| D3 | Component test |
| D4 | Integrated service |
| D5 | Actual application/runtime |
| D6 | Cross-app real user workflow |
| D7 | Target hardware |
| D8 | Sustained real-world use |

---

## 10. Golden Journeys (canonical 1–10)

1. Student assignment → recreation  
2. Offline → reconnect  
3. Creator build/package/install  
4. Office dock  
5. Handheld play → dock → work → undock  
6. DS-XL dual-screen coding  
7. Ring real input  
8. Private local AI tutoring  
9. Failed update rollback  
10. Lost-device revoke  

Device Lab ECO journeys are engineering verification and **do not** replace these user Golden Journeys. Canonical machine list: `program/operating_model/02_QUALITY_USERS/GOLDEN_JOURNEYS.json`.

---

## 11. Completion vs release ladder

| Stage | Meaning |
|---|---|
| Product definition complete | Charter, ownership, claim boundaries, journeys linked — **requires Edmund merge** for approval token |
| Digital implementation complete | Code/integration digitally validated (≤E4 as earned) |
| Pre-EVT virtual validation | Device Lab / digital twin depth |
| EVT | First engineering validation hardware |
| DVT | Design validation |
| PVT | Production validation |
| Certification | Regulatory/lab |
| Carrier acceptance | External operator acceptance |
| Pilot | Real users / campuses |
| Production | Manufacturing release |
| Operation | Sustained field evidence (E8) |

Cycle 3A does **not** start `WP-001` (EVT0 freeze). Preview only: `artifacts/wp012/WP-001_INPUT_MANIFEST_PREVIEW.json`.

---

## 12. Authority and approval

- **Canonical narrative + YAML:** this directory.  
- **Ecosystem Portal:** `gunnchos-research-portal` (navigation; not a competing charter).  
- **Profile front door:** `gunnchOS3k` README.  
- **Historical spine ingest:** `program/charters/` and workspace spine markdown — labeled historical when conflicting.  
- **Approval event:** Edmund’s merge of the final Product Charter PR. Until then:
  - `definition_content_complete_candidate` may be true  
  - `PRODUCT_CHARTER_DEFINITION_COMPLETE` remains **false**  
  - `owner_approval_token` remains **false**

---

## 13. Related artifacts (WP-012)

- `artifacts/wp012/PROJECT_CHARTER_COMPLETION_REGISTER.json`  
- `artifacts/wp012/PROJECT_CHARTER_REMAINING_REAL_WORLD_GAPS.md`  
- `artifacts/wp012/REPO_CATALOG.yaml` / `REPO_CATALOG.md`  
- `artifacts/wp012/WP-001_INPUT_MANIFEST_PREVIEW.json`  
- `artifacts/cycle3a/ACCEPTED_MAIN_BASELINE.json`  
