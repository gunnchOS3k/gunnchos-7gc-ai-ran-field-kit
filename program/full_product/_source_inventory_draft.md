# Full Product Source Totality Inventory (Draft)

**Audit date:** 2026-08-07  
**Repos root:** `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos`  
**Primary integration repo:** `gunnchos-7gc-ai-ran-field-kit`  
**Method:** Read-only filesystem inventory of normative product sources. Documents are listed only if they exist on disk. Estimates of MUST/SHALL/required language are approximate (keyword + structured-ID counts).

**Normative counting legend**

| Symbol | Meaning |
|--------|---------|
| `~N rfc` | Approximate matches of MUST/SHALL/must/shall (case-insensitive where noted) |
| `~N req-word` | Approximate matches of “required/requirement” |
| `~N bullets` | Approximate markdown bullet / checklist lines (proxy for soft requirements) |
| `N IDs` | Explicit structured requirement IDs (e.g. `SYS-MISSION-001`) |

---

## 0. Executive findings (do not invent)

1. **Carrier-Grade charter exists** and is ingested into field-kit as the Gate 0 authority. It also embeds **Four-Game Platform Requirements (charter §8)** and **Gates 0–8 (charter §11)**. There is **no separate file** named “Four-Game Master Requirements” or a cross-game GDD under `repos/`.
2. **Per-game requirement/GDD packs exist** in the four game repos; depth varies (Anime Aggressors richest; Pedestrian MVP-forward; Beat Link has an explicit GDD; Archive is data/science-normative).
3. **Formal product requirement corpus** in field-kit `program/requirements/requirements.yaml` has **419 IDs** derived from the charter; registry marks **396 NOT_STARTED** and **23 DOCUMENTED_DESIGN** for `implementation_state` (none IMPLEMENTED in that taxonomy).
4. **Sibling game code reality is ahead of that taxonomy** for MVP/core-loop slices (playable Godot / web / Capacitor prototypes), while **device/OS/ring/dock full-product requirements remain largely DOC_ONLY or STUB** relative to charter claims.
5. **`EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon` is ownership-canonical in policy YAMLs but is not present** under this `repos/` tree.
6. **`gunnchOS3k` local checkout is a profile/quality/evidence shell**, not the device OS implementation; **`gunnchos-device-os` holds OS requirements and dock/OS code**.
7. **Hardware formal ADR-\* files are scarce**; field-kit uses `DR-0001`…`DR-0005`; Anime Aggressors has `ADR-0001`/`ADR-0002`. Hardware industrial-design repo uses docs + BOMs + CAD, not an ADR series.

---

## 1. Source document inventory

### 1.1 Product charter (ecosystem spine)

| Absolute path | Description | Normative estimate | Slice / conflict language |
|---|---|---|---|
| `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/program/charters/GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md` | **gunnchOS3k Carrier-Grade 6G Equitable Compute Ecosystem** — primary product charter (devices, rings, OS, AI, connectivity, 7GC, four games, manufacturing/evidence, Gates 0–8). | ~26 rfc + ~8 req-word; ~442 bullets; **419 structured IDs extracted** | Success ≠ four APKs; each game needs reliable **core loop**; Gate 1 = core loops; Gate 2 = **device vertical slices**; full operational product requires 16 workstreams (§10). |
| `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/program/charters/CHARTER_SOURCE_RECORD.yaml` | Ingestion provenance for charter (`sha256`, line count 834). | N/A (meta) | Notes source filename outside git. |
| `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/program/charters/CHARTER_APPROVAL_RECORD.yaml` | Charter approval status record. | N/A | Product charter approval still a Gate 0 blocker class elsewhere (`PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND`). |

**Not found:** standalone file titled “Four-Game Master Requirements” or “Four-Game GDD” outside charter §8.

---

### 1.2 Field-kit structured requirements, decisions, gates, claims

| Absolute path | Description | Normative estimate | Slice / conflict language |
|---|---|---|---|
| `.../gunnchos-7gc-ai-ran-field-kit/program/requirements/requirements.yaml` | Canonical structured requirement set (charter-derived). | **419 IDs** | `implementation_state`: 396 NOT_STARTED, 23 DOCUMENTED_DESIGN; `claim_state` mostly TARGET. |
| `.../program/requirements/requirement_source_map.yaml` | Line-range mapping ID → charter section. | 419 mappings | — |
| `.../program/requirements/requirement_ownership.yaml` | Owner repo per requirement. | 419 | References EdgeGesture owner for many ring reqs (repo not local). |
| `.../program/requirements/requirement_verification_methods.yaml` | Verification method catalog. | large | — |
| `.../program/requirements/requirement_dependencies.yaml` | Dependency graph among reqs. | large | — |
| `.../program/requirements/device_role_baseline.yaml` | Device role freeze baseline. | small | Aligns Student 14.5 / DS-XL / Handheld / Rings. |
| `.../program/requirements/requirements.schema.json` | Schema for requirements.yaml. | N/A | — |
| `.../program/decisions/DR-0001-INTEGRATION-AUTHORITY.md` | Field-kit as integration authority. | decision | — |
| `.../program/decisions/DR-0002-DEVICE-ROLE-BASELINE.md` | Device role baseline decision. | decision | — |
| `.../program/decisions/DR-0003-CLAIM-CLASSIFICATION.md` | Claim taxonomy decision. | decision | — |
| `.../program/decisions/DR-0004-RING-WORKSTREAM-OWNERSHIP.md` | Ring workstream ownership. | decision | Points EdgeGesture vs hardware/OS split. |
| `.../program/decisions/DR-0005-CANONICAL-REPOSITORY-SET.md` | Canonical repo set incl. four games. | decision | Explicitly includes four games + EdgeGesture. |
| `.../program/gates/gate_definitions.yaml` | Gate 0–8 names/summaries. | 9 gates | Gate 1: OS/ring/dock/AI/**game core loops**; Gate 2: **vertical slices**. |
| `.../program/gates/gate_status.yaml` | Live gate status registry. | — | — |
| `.../program/gates/gate_dependency_graph.yaml` | Gate dependency graph. | — | — |
| `.../program/gates/external_gate_registry.yaml` | External gate registry. | — | — |
| `.../program/gates/physical_gate_registry.yaml` | Physical gate registry. | — | — |
| `.../program/gates/human_action_registry.yaml` | Human-action gate registry. | — | — |
| `.../program/claims/claims.yaml` | Claim registry. | — | — |
| `.../program/claims/claim_taxonomy.yaml` | Claim classes. | — | — |
| `.../program/claims/CLAIM_FIREWALL.md` | Claim firewall narrative. | — | — |
| `.../program/claims/prohibited_claim_patterns.yaml` | Prohibited 6G/overclaim patterns. | — | — |
| `.../program/reports/GATE_0_REQUIREMENTS_TRACEABILITY_MATRIX.md` | Human-readable RTM for Gate 0 corpus. | 419 rows | Many TARGET + physical blockers. |
| `.../program/reports/GATES_0_TO_8_TOTALITY_TRACEABILITY.md` | Nonphysical totality vs physical freeze. | — | Declares NONPHYSICAL complete; physical PASS pending. |
| `.../program/reports/GATES_1_TO_8_BASELINE.md` | Gates 1–8 baseline report. | — | — |
| `.../program/reports/GATE_0_*.md` | Gate 0 audits/completion/claims/ownership. | — | — |
| `.../program/backlog/master_gap_backlog.yaml` | Gap backlog tied to requirement blockers. | many gaps | — |
| `.../NON_NEGOTIABLES_GATES_4_6.md` | Gates 4–6 non-negotiables (research/acceptance). | ~1 rfc | Research-spine oriented. |
| `.../ROLE_REQUIREMENT_TRACEABILITY.md` | Role→requirement traceability. | small | — |
| `.../EXTERNAL_GATE_REGISTRY.json` | External gate registry (JSON). | — | — |
| `.../requirements/sources/README.md` | Gates 4–6 external source links (Oulu/NVIDIA). | links only | Points to attached Gates 4–6 acceptance doc (not copied into repo). |

---

### 1.3 Gate catalogs (field-kit `gate1`…`gate8`)

| Absolute path | Description | Normative estimate | Notes |
|---|---|---|---|
| `.../gate1/README.md` | Gate 1 overview. | short | Integrated platform / core loops. |
| `.../gate1/manifests/gate1_*.yaml` | Components, services, test matrix, physical evidence reqs. | structured | Includes game instrumentation / physical evidence. |
| `.../gate1/reports/*.md` | Gate 1 audits, packets, matrices (many). | process | Mix of research pilot + product Gate 1. |
| `.../gate1/ring_fabrication/README.md` | Ring fabrication packet pointer. | — | — |
| `.../gate2/GATE_2_EXECUTION_PACKET.md` | Gate 2 execution packet. | — | Device vertical slices. |
| `.../gate2/GATE_2_ENTRY_BLOCKERS.md` | Entry blockers. | — | — |
| `.../gate2/nonphysical/README.md` + `G2_C1`…`G2_C7` | Nonphysical Gate 2 capability packets (enclosure, display, battery/thermal, secure boot, signed update, device/game UX, ring calibration). | per-capability | UX product-quality contract under `G2_C6`. |
| `.../gate3/GATE_3_*.md` + `nonphysical/G3_C*` | Ecosystem alpha packets (identity continuity, threat models, 7GC plans, repair). | — | — |
| `.../gate4/README.md` + participants/privacy/governance/incidents/ntn/accessibility | Field pilot nonphysical catalog. | many injects | Explicit human/ethics blockers upstream. |
| `.../gate5/README.md` + dfm/regulatory/carrier/provisioning/supply_chain | Preproduction packets. | — | — |
| `.../gate6/README.md` + support_lifecycle/release/defects | RC packets. | — | — |
| `.../gate7/README.md` + submission_books/*/BOOK.md + vuln_response | Deployment submission books. | — | — |
| `.../gate8/README.md` + `standards/` | Standards / IMT-2030 migration readiness. | — | — |
| `.../standards/sources.yaml` + `requirements/imt2030_current_state.yaml` + snapshots | Standards source catalog. | — | Honest 6G language. |

Root-level research Gate docs also exist (`GATE1_LOCKED_RESEARCH_THESIS.md`, `GATE2_*`, `GATE3_*`, `GATE4_*`, `GATES_4_6_*`) — these are **AI-RAN field-kit research gates**, overlapping names with product Gates 0–8; treat as parallel research track unless cross-linked.

---

### 1.4 Four games — requirements / GDD / quality

#### Pedestrian Pursuit

| Absolute path | Description | Normative estimate | Slice language |
|---|---|---|---|
| `.../pedestrian-pursuit/docs/GAME_REQUIREMENTS.md` | Thin index to MVP/pillars/controls/architecture/roadmap/acceptance. | ~1 must | Defers to MVP docs. |
| `.../pedestrian-pursuit/docs/MVP_SCOPE.md` | MVP checklist (mostly checked). | ~20 checklist items | **Out of Scope (Stretch Goals)** explicit. |
| `.../pedestrian-pursuit/docs/ACCEPTANCE_CRITERIA.md` | MVP acceptance criteria. | ~35 checkboxes | MVP accepted when listed items true. |
| `.../pedestrian-pursuit/docs/DESIGN_PILLARS.md` | Design pillars. | short | — |
| `.../pedestrian-pursuit/docs/CONTROLS.md` | Controls. | — | — |
| `.../pedestrian-pursuit/docs/TECHNICAL_ARCHITECTURE.md` | Architecture. | — | — |
| `.../pedestrian-pursuit/docs/ROADMAP.md` | Roadmap. | — | — |
| `.../pedestrian-pursuit/docs/PRODUCTION_READINESS_REPORT.md` | Production readiness. | — | **“Playable vertical slice (Godot); Android blocked.”** |
| `.../pedestrian-pursuit/docs/product-quality/*` | Product-quality / Pixel evidence. | — | — |
| `.../pedestrian-pursuit/device_ux/README.md` | Device UX roles for Gate UX. | — | — |
| Charter §8.4 (in field-kit charter) | Full-product Pedestrian requirements (body-as-vehicle, rings, cross-device). | part of 419 IDs (`GAME-PP-*`) | Broader than MVP_SCOPE. |

**Not found:** dedicated Pedestrian `GAME_DESIGN_DOCUMENT.md` / `GDD.md`.

#### Beat Link / BeatLink Party

| Absolute path | Description | Normative estimate | Slice language |
|---|---|---|---|
| `.../beatlink-party/docs/GAME_DESIGN_DOCUMENT.md` | **Beat Link GDD** (roles, modes, scoring, MVP scope). | ~71 lines; MVP sections | Explicit **MVP** host/player/role scope. |
| `.../beatlink-party/docs/PRODUCT_REQUIREMENTS.md` | Product requirements + MVP functional status table. | ~13 bullets; table marks Implemented/Planned | In-memory rooms MVP; Redis/Postgres later. |
| `.../beatlink-party/docs/API_SPEC.md` | MVP API specification. | ~113 lines | — |
| `.../beatlink-party/docs/MUSIC_COMPLIANCE.md` | Music/compliance non-negotiables. | — | No ripping platform audio. |
| `.../beatlink-party/docs/ROADMAP.md` | Phased roadmap. | — | Phase 1–2 marked MVP complete. |
| `.../beatlink-party/docs/TEST_PLAN.md` | Test plan. | — | MVP performance targets. |
| `.../beatlink-party/device_ux/README.md` | Device UX. | — | — |
| Charter §8.2 | Full-product Beat Link experience requirements. | `GAME-BEATLINK-*` IDs | Broader than MVP (calibration, rematch, device expression matrix). |

#### Archive of Life

| Absolute path | Description | Normative estimate | Slice language |
|---|---|---|---|
| `.../archive-of-life-artifact-world/docs/EXTERNAL_DATA_REQUIREMENTS.md` | External scientific data requirements. | ~14 soft-reqs | Source authority list. |
| `.../archive-of-life-artifact-world/docs/FULL_IMPLEMENTATION_DEFINITION.md` | Status vocabulary (FULLY_IMPLEMENTED…PLANNED_NOT_STARTED). | policy | Prevents overclaiming completeness. |
| `.../archive-of-life-artifact-world/docs/IMPLEMENTATION_STATUS.md` | Implementation status narrative. | — | — |
| `.../archive-of-life-artifact-world/docs/ARCHIVEDEX_*.md` | Species entry / progressive reveal / schema. | — | — |
| `.../archive-of-life-artifact-world/docs/DATA_*.md` + `SOURCE_*.md` + `NASA_*.md` + coverage matrices | Data architecture, provenance, NASA Earth systems, coverage. | many | Mock vs verified data split. |
| `.../archive-of-life-artifact-world/docs/product-quality/*` | Acceptance / limitations / Pixel evidence. | — | Known limitations documented. |
| `.../archive-of-life-artifact-world/device_ux/README.md` | Device UX. | — | — |
| Charter §8.3 | Known-record-of-life + scientific record fields. | `GAME-AOL-*` | Explicitly forbids claiming all species ever existed. |

**Not found:** single Archive `GDD.md` (design spread across data/product docs).

#### Anime Aggressors

| Absolute path | Description | Normative estimate | Slice language |
|---|---|---|---|
| `.../anime-aggressors/docs/PRODUCT_REQUIREMENTS.md` | Canonical PRD; Tracks A–H full-completion program. | ~68 bullets; ~22 rfc-ish words | **“No longer scoped only as v0.1 vertical slice”** but Track A remains first shippable proof; **§8 MVP/v0.1 vertical slice**; completing A ≠ completing product. |
| `.../anime-aggressors/docs/PLATFORM_FIGHTER_REQUIREMENTS.md` | Platform fighter requirements. | ~36 bullets | — |
| `.../anime-aggressors/docs/CONSOLE_PLATFORM_FIGHTER_UX_SPEC.md` | Console/platform fighter UX spec. | ~468 lines | — |
| `.../anime-aggressors/docs/WEARABLE_PRODUCT_REQUIREMENTS.md` | Wearable product requirements. | ~14 soft-reqs | Optional wearables. |
| `.../anime-aggressors/docs/ROADMAP_FULL_COMPLETION.md` | Full-completion roadmap Tracks A–H. | ~220 lines | Vertical slice honesty vs full product. |
| `.../anime-aggressors/docs/fighters/*` | Per-fighter production/FIGHTER specs. | many | — |
| `.../anime-aggressors/docs/decisions/ADR-0001-firmware-stack.md` | Firmware stack ADR. | ADR | — |
| `.../anime-aggressors/docs/decisions/ADR-0002-desktop-shell.md` | Desktop shell ADR. | ADR | — |
| `.../anime-aggressors/hardware/ring/REQUIREMENTS.md` | Ring hardware requirements. | — | — |
| `.../anime-aggressors/hardware/wristband/REQUIREMENTS.md` | Wristband requirements. | — | — |
| `.../anime-aggressors/device_ux/README.md` | Device UX. | — | — |
| Charter §8.5 | Full-product Anime Aggressors requirements. | `GAME-AA-*` | Includes fairness proof for ring competitive control. |

---

### 1.5 gunnchOS / device OS

| Absolute path | Description | Normative estimate | Notes |
|---|---|---|---|
| `.../gunnchos-device-os/GUNNCHOS_REQUIREMENTS_v0.1.md` | Early gunnchOS requirements narrative. | ~42 bullets / ~4 rfc | — |
| `.../gunnchos-device-os/REQUIREMENTS.md` | Pointer stub (“see manufacture-ready…”). | ~18 lines | Thin. |
| `.../gunnchos-device-os/requirements/*.md` | Shippable OS requirement pack (boot, security, offline, gaming, school, GA, RC, etc.). | **~285 bulletish** across ~20 files | Primary OS normative set. |
| `.../gunnchos-device-os/docs/PRODUCT_REQUIREMENTS_SUMMARY.md` | Summary. | short | — |
| `.../gunnchos-device-os/docs/DEVICE_SPECIFIC_OS_BEHAVIOR.md` | Per-device OS behavior. | — | — |
| `.../gunnchos-device-os/docs/6G_URLLC_REQUIREMENTS_MATRIX.md` | URLLC matrix. | — | Claim-sensitive. |
| `.../gunnchos-device-os/docs/gate1/DOCK_CONTINUITY.md` | Dock continuity Gate 1 doc. | — | Aligns charter dock continuity. |
| `.../gunnchos-device-os/product/*.md` | Product-facing requirement mirrors. | — | Some duplication vs `requirements/`. |
| `.../gunnchos-device-os/qa/QA_MASTER_TEST_PLAN.md` | QA master plan. | — | — |
| `.../gunnchOS3k/README.md` + `docs/*` + `quality/*` | Org profile / evidence standards / claim downgrades — **not a full OS product GDD**. | quality/governance | Local tree lacks OS implementation sources. |

Charter §§5–7 OS/AI/connectivity services map to field-kit IDs `OS-*`, `AI-*`, `CONN-*`.

---

### 1.6 gunnchAI3k

| Absolute path | Description | Normative estimate | Notes |
|---|---|---|---|
| `.../gunnchAI3k/docs/00_GUNNCHAI3K_TUTOR_VISION.md` … `19_*.md` | Numbered tutor/policy doc set. | **Mostly stubs (3 lines)** pointing to `prompts/` / `src/tutor/` | Titles exist; body content largely **not filled**. |
| `.../gunnchAI3k/docs/AUDIT_FEATURE_MATRIX.md` | Feature audit matrix. | thin | — |
| `.../gunnchAI3k/docs/PROOF_OF_OPERATION.md` / `LAUNCH_*` / Discord checklists | Operational proof / launch docs. | operational | Discord-tutor oriented more than device-local AI charter. |
| `.../gunnchAI3k/README.md` + root study/JARVIS summaries | Product narrative / feature summaries. | — | Mixed maturity. |
| `.../gunnchAI3k/LEARNING_SYSTEM.md` | Learning system. | — | — |
| `.../gunnchAI3k/SECURITY.md` | Security. | — | — |
| Charter §6 | gunnchAI3k intelligent system layer + local-first + governance. | `AI-CORE-*`, `AI-LOCAL-*`, `AI-GOV-*` | Broader than Discord tutor stubs. |

---

### 1.7 Manufacturing / hardware industrial design (normative + research)

| Absolute path | Description | Normative estimate | Notes |
|---|---|---|---|
| `.../gunnchos-hardware-industrial-design/REQUIREMENTS.md` | Stub pointer. | tiny | — |
| `.../gunnchos-hardware-industrial-design/docs/00_START_HERE.md` … `16_*.md` | Device family vision, architecture, BOM/cost, EVT/DVT/PVT, 7GC node model, etc. | mixed; several `*_PLACEHOLDER.md` siblings | Placeholders exist — do not treat placeholders as filled requirements. |
| `.../gunnchos-hardware-industrial-design/docs/DEVICE_REQUIREMENTS.md` | Device requirements (thin/alias). | tiny | — |
| `.../gunnchos-hardware-industrial-design/docs/06_DEVICE_REQUIREMENTS.md` | Device requirements chapter. | short | — |
| `.../gunnchos-hardware-industrial-design/docs/device-quartet/*-research-spec.md` | Research specs for Student 14.5, DS-XL, Handheld, Edge I/O wearables. | ~50–56 lines each | Research-spec depth, not full RFC corpus. |
| `.../gunnchos-hardware-industrial-design/docs/12_BOM_AND_COST_TARGETS.md` | BOM/cost targets. | — | — |
| `.../gunnchos-hardware-industrial-design/docs/BILL_OF_MATERIALS.md` | BOM narrative. | — | — |
| `.../gunnchos-hardware-industrial-design/firmware_os_interface/*REQUIREMENTS.md` | Secure boot, TPM, recovery, input enumeration, firmware/OS interface. | — | — |
| `.../gunnchos-hardware-industrial-design/os_compatibility/*REQUIREMENTS.md` | OS compatibility requirement packs. | — | — |
| `.../gunnchos-hardware-industrial-design/mechanical_correctness/*REQUIREMENTS.md` | Mechanical correctness packs. | — | — |
| `.../gunnchos-hardware-industrial-design/thermal/THERMAL_REQUIREMENTS.md` | Thermal requirements. | — | — |
| `.../gunnchos-hardware-industrial-design/manufacturing/*.md` | Manufacturing readiness / EVT-DVT-PVT / quality / repair plans. | process | — |
| `.../gunnchos-hardware-industrial-design/versions/production_candidate/*REQUIREMENTS.md` | Production candidate requirements/policies. | — | — |
| `.../gunnchos-7gc-ai-ran-field-kit/device_designs/*/requirements.yaml` | Per-device Gate 2 digital definition requirements. | structured | Student 14.5, DS-XL, Handheld, Rings. |
| `.../gunnchos-7gc-ai-ran-field-kit/device_designs/*/architecture.md` + ICD + BOM CSV + mechanical README | Device digital design packets. | — | SCAD enclosures present. |
| `.../gunnchos-7gc-ai-ran-field-kit/program/physical/MASTER_*` + `MASTER_PROCUREMENT_BOM.csv` | Physical build/test/acceptance books + procurement BOM. | process | Physical execution freeze active per totality report. |

---

### 1.8 7GC / research product spine docs

| Absolute path | Description | Normative estimate | Notes |
|---|---|---|---|
| `.../docs/7gc/7GC_MASTER_INDEX.md` | 7GC master index. | short | Workspace `docs/` (not inside field-kit git alone). |
| `.../docs/7gc/7GC_EVIDENCE_MATRIX.md` | Evidence matrix. | — | — |
| `.../docs/7gc/7GC_NON_CLAIM_POLICY.md` | Non-claim policy. | — | Critical for honesty. |
| `.../docs/7gc/7GC_REPO_MAP.md` | Repo map. | — | — |
| `.../docs/7gc/7GC_SITE_COMPLETION_MATRIX.md` | Site completion matrix. | — | — |
| `.../docs/7gc/CROSS_REPO_HANDOFF.md` + `sites/*/CROSS_REPO_HANDOFF.md` | Site handoffs. | — | — |
| `.../docs/campus_design/7GC_EXPERT_REVIEW_REQUIREMENTS.md` | Expert review requirements. | — | — |
| `.../7gc-digital-twin/paper/*.md` | Digital twin paper/system model/methodology. | research | — |
| `.../7gc-digital-twin/quality/*.md` | Reality audit, gap analysis, claims downgraded. | quality | — |
| `.../gunnchos-7gc-ai-ran-field-kit/docs/SOURCE_MATRIX.md` | 60-source research package matrix. | research | Many `[TBD]`. |
| `.../gunnchos-7gc-ai-ran-field-kit/docs/SYSTEM_OVERVIEW.md` | System overview. | — | — |
| `.../gunnchos-7gc-ai-ran-field-kit/docs/CLAIMS_TO_EVIDENCE.md` | Claims→evidence. | — | — |
| Charter §7.3 | Seven Global Campus role requirements. | campus eval bullets | Equal excellence via locally appropriate infrastructure. |

---

### 1.9 READMEs (entry points — selected)

| Absolute path | Role |
|---|---|
| `.../gunnchos-7gc-ai-ran-field-kit/README.md` | Primary field-kit entry. |
| `.../gunnchos-hardware-industrial-design/README.md` | Hardware repo entry. |
| `.../gunnchos-hardware-industrial-design/device_designs/README.md` | Points to field-kit `device_designs/` as Gate 2 digital definition; physical pending. |
| `.../gunnchos-device-os/requirements/README.md` | OS requirements index. |
| `.../pedestrian-pursuit/README.md` | Game entry. |
| `.../beatlink-party/README.md` | Game entry. |
| `.../archive-of-life-artifact-world/README.md` | Game entry. |
| `.../anime-aggressors/README.md` | Game entry. |
| `.../gunnchAI3k/README.md` | AI entry. |
| `.../gunnchOS3k/README.md` | Org/profile entry. |
| `.../edge-io-measurement-node/gate1_digital_fabrication/README.md` | Ring firmware fabrication entry. |

---

## 2. Conflicts and slice-vs-full-product language (cross-cutting)

| Conflict | Where it appears | Implication |
|---|---|---|
| **MVP / vertical slice vs full product** | Pedestrian `MVP_SCOPE` + production “vertical slice”; Beat Link MVP PRD/GDD; Anime PRD Track A / “completing A does not complete product”; charter Gate 1 “one core loop” vs Gate 2+ full device/ecosystem | Game repos can honestly claim MVP/core-loop progress without satisfying charter full-device, multiplayer, ring, accessibility, or continuity requirements. |
| **Charter “not merely four APKs”** | Charter §8 | Launching APKs/web builds ≠ Gate pass for games. |
| **Formal requirements.yaml vs sibling code** | `implementation_state` all NOT_STARTED/DOCUMENTED_DESIGN | Taxonomy is charter-traceability honest for **ecosystem claims**; it under-represents **local MVP code** unless mapped with a secondary “prototype evidence” class. |
| **Nonphysical totality COMPLETE vs physical PASS PENDING** | `GATES_0_TO_8_TOTALITY_TRACEABILITY.md` | Docs/packets ≠ manufactured/validated product. |
| **Hardware digital artifacts ≠ GATE_2_PASS** | hardware `device_designs/README.md` | Explicit ban on claiming Gate 2 pass from digital-only. |
| **Archive “known record” vs completeness** | Charter §8.3 + Archive FULL_IMPLEMENTATION_DEFINITION | Scientific completeness claims forbidden; mock data ≠ verified coverage. |
| **Music links ≠ rip rights** | Charter §8.2 + Beat Link MUSIC_COMPLIANCE | Compliance non-negotiable. |
| **gunnchAI numbered docs stubs vs charter AI platform** | `gunnchAI3k/docs/00–19` mostly 3-line stubs | Policy surface incomplete relative to `AI-*` IDs. |
| **EdgeGesture ownership without local clone** | ownership YAMLs | Ring sensing requirements orphaned in this workspace. |
| **Name collision: research Gates 1–4 vs product Gates 0–8** | field-kit root `GATE*.md` vs `program/gates` + charter §11 | Easy to conflate AI-RAN research gates with product ecosystem gates. |
| **gunnchOS3k vs gunnchos-device-os** | two repos | OS product requirements live primarily in device-os. |

---

## 3. Hardware ADRs / BOMs / CAD (Student 14.5, DS-XL, Handheld, Rings, Dock)

### 3.1 Decision records / ADRs

| Location | What exists |
|---|---|
| `.../gunnchos-7gc-ai-ran-field-kit/program/decisions/DR-0001` … `DR-0005` | Ecosystem DRs (integration, roles, claims, rings, repos). **Not hardware schematic ADRs.** |
| `.../anime-aggressors/docs/decisions/ADR-0001-firmware-stack.md` | Wearable firmware stack. |
| `.../anime-aggressors/docs/decisions/ADR-0002-desktop-shell.md` | Desktop shell. |
| `.../spectrumx-ai-ran-gary/docs/uml/architecture_decisions.md` | Research UML architecture decisions (AI-RAN), not device quartet ADRs. |
| **Not found under hardware-industrial-design** | No `ADR-*.md` series located. |

### 3.2 BOMs

| Device / scope | Absolute path(s) |
|---|---|
| Master BOM index | `.../gunnchos-hardware-industrial-design/bom/MASTER_BOM.md` |
| Student 14.5 | `.../bom/student_14_5/bom.csv`, `bom_assembly.csv`; also `bom/student_14_5_bom.csv`; field-kit `device_designs/student_14_5/component_bom.csv` |
| DS-XL Coder | `.../bom/ds_xl_coder/bom.csv`, `bom_assembly.csv`; `bom/ds_xl_coder_bom.csv`; field-kit `device_designs/ds_xl_coder/component_bom.csv` |
| Handheld Hybrid | `.../bom/handheld_hybrid/bom.csv`, `bom_assembly.csv`; `bom/handheld_hybrid_bom.csv`; field-kit `device_designs/handheld_hybrid/component_bom.csv` |
| Rings / wearables arena | `.../bom/wearables_arena_set/bom.csv`, `bom_assembly.csv`; `bom/wearables_arena_bom.csv`; field-kit `device_designs/edge_io_rings/component_bom.csv`; gate1 ring assembly BOMs under `gate1_digital_fabrication/edge_io_ring/bom/` and `pcb/assembly/` |
| Anime Aggressors ring/wristband | `.../anime-aggressors/hardware/ring/bom.csv` (+ `bom/edgeio-ring-target-bom.csv`); wristband `bom.csv` / `dev-board-mule-bom.csv` |
| Edge I/O measurement node | `.../edge-io-measurement-node/hardware/bom_template.csv` |
| Field-kit procurement | `.../gunnchos-7gc-ai-ran-field-kit/program/physical/MASTER_PROCUREMENT_BOM.csv` |
| Assumptions | `.../gunnchos-hardware-industrial-design/bom/BOM_ASSUMPTIONS.md` |

### 3.3 CAD / electrical / mechanical

| Device | CAD / mechanical | Electrical / KiCad | Notes |
|---|---|---|---|
| Student 14.5 | `.../hardware.../cad/` + `devices/student_14_5/`; `manufacturing/student_14_5/`; field-kit `device_designs/student_14_5/mechanical/student_14_5_enclosure.scad`; STL placeholder `exports/stl/student_14_placeholder.stl` | `electrical/student_14_5/kicad/*`; `schematics/student_14/` | Also `schematics/student_14/` block schematic. |
| DS-XL | `devices/ds_xl_coder/`; field-kit `ds_xl_coder_enclosure.scad`; STL placeholder | `electrical/ds_xl_coder/kicad/*`; `schematics/ds_xl_coder/` | — |
| Handheld | `devices/handheld_hybrid/`; field-kit `handheld_hybrid_enclosure.scad`; STL placeholder | `electrical/handheld_hybrid/kicad/*`; `schematics/handheld_hybrid/` | — |
| Rings | `gate1_digital_fabrication/edge_io_ring/mechanical/` (`.stl`, `.step.txt`); `devices/wearables_arena_set/`; field-kit `edge_io_rings_enclosure.scad` | `electrical/wearables_arena_set/kicad/*`; ring EVT0 kicad under `gate1_digital_fabrication/edge_io_ring/` | Firmware companion: `edge-io-measurement-node/gate1_digital_fabrication/ring_firmware/` |
| Dock | **No dedicated dock CAD/BOM device folder found** under hardware `devices/` or field-kit `device_designs/`. Dock is primarily **OS/continuity**: `gunnchos-device-os/gate1_digital_fabrication/dock/` (topology, collectors), `docs/gate1/DOCK_CONTINUITY.md`, `gunnchos_device_os/dock_manager.py`, schemas/evidence JSON. Charter treats dock as platform capability (Student/Handheld), not a fifth named industrial-design SKU in local CAD tree. |

### 3.4 Field-kit mirrored device packets

`/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/device_designs/{student_14_5,ds_xl_coder,handheld_hybrid,edge_io_rings}/` each contain: `architecture.md`, `requirements.yaml`, `block_diagram.md`, `interface_control_document.md`, `component_bom.csv`, `electrical/`, `firmware/`, `mechanical/`, `manufacturing/`, `os/`, `validation/`.

---

## 4. Top 50 highest-priority unmapped product requirements vs code reality

**Basis:** Charter-derived P0 IDs in `requirements.yaml` (all formally NOT_STARTED/DOCUMENTED_DESIGN) + honest sibling-repo evidence.  
**Guess labels:** `DOC_ONLY` (spec/packet only) · `STUB` (scaffold/partial) · `IMPLEMENTED` (MVP/prototype exists but may not meet full charter) · `MISSING_REPO` (owner not in workspace).

| # | ID / theme | Why priority | Honest code guess |
|---|---|---|---|
| 1 | SYS-MISSION-004 — gunnchOS on every first-party device | Gate 1 entry | **STUB** — device-os has services/tests; no quartet physical boot evidence |
| 2 | SYS-MISSION-005 — embed gunnchAI3k local-first | Gate 1 | **STUB** — Discord/tutor code exists; device-local runtime not charter-complete |
| 3 | SYS-MISSION-007 — rings as usable input environments | Gate 1 | **STUB/MISSING_REPO** — firmware/BOM/digital fab exist; EdgeGesture absent; physical pending |
| 4 | DEV-HANDHELD-002…010 — dock transition continuity set | P0 Gate 1 | **STUB** — dock_manager + continuity tests/docs; not full app/session/AI/multiplayer preservation |
| 5 | OS-PLATFORM-001 — unified user identity | OS platform | **STUB** |
| 6 | OS-PLATFORM-004 — ring input service | OS platform | **STUB** |
| 7 | OS-PLATFORM-006 — display and dock manager | OS platform | **STUB** (dock_manager present) |
| 8 | OS-PLATFORM-007 — cross-device session continuity | OS platform | **STUB** |
| 9 | OS-PLATFORM-010 — local AI runtime | OS platform | **DOC_ONLY/STUB** |
| 10 | OS-PLATFORM-011 — connectivity orchestrator | OS + charter §7.2 | **DOC_ONLY/STUB** |
| 11 | OS-PLATFORM-014…018 — secure boot / measured boot / OTA / rollback / recovery | Security Gate 3 | **DOC_ONLY/STUB** — packets + firmware_os_interface docs; physical validation pending |
| 12 | RING-AWARE-002…011 — wearer/device/surface awareness | Ring core | **DOC_ONLY** / **MISSING_REPO** sensing owner |
| 13 | RING-INPUT-003…021 — productivity inputs | Ring productivity | **DOC_ONLY** |
| 14 | RING-INPUT-023…036 — gaming inputs | Ring gaming | **STUB** — Anime firmware/protocol sketches; not fair competitive proof |
| 15 | RING-RELIAB-001…015 — calibration/confidence/anti-spoof/offline | Reliability | **DOC_ONLY** (G2_C7 packet exists) |
| 16 | AI-CORE-001 — personalized tutoring | AI P0 | **STUB/IMPLEMENTED** Discord/tutor path; not device-family embedded |
| 17 | AI-CORE-002 — code assistance | AI P0 | **STUB** |
| 18 | AI-CORE-005 — game coaching | AI P0 | **DOC_ONLY** |
| 19 | AI-CORE-006/007 — network optimization / path recommendations | AI P0 | **DOC_ONLY** |
| 20 | AI-LOCAL-001…010 — offline local-first AI pack | Local-first | **DOC_ONLY/STUB** |
| 21 | AI-LOCAL-011 — cloud not sole path | Local-first | **DOCUMENTED_DESIGN** only |
| 22 | GAME-BEATLINK-001…005 — host room / join / legal source / roles / timing cal | Beat Link P0 | **IMPLEMENTED** (MVP web) for 001–004; **STUB** for production timing calibration |
| 23 | GAME-BEATLINK reconnect/rematch + device expression matrix | Charter beyond MVP | **DOC_ONLY/STUB** |
| 24 | GAME-AOL scientific record fields (canonical ID…citation) | Archive P0 | **STUB/IMPLEMENTED** schema+pipelines; verified full corpus **DOC_ONLY** / blocked by external data |
| 25 | GAME-AOL known-record-without-completeness-claim | Integrity | **IMPLEMENTED** as policy/docs + status labels |
| 26 | GAME-PP core loop (body/feet racer) | Pedestrian P0 | **IMPLEMENTED** Godot MVP core loop; Android export issues noted |
| 27 | GAME-PP multiplayer / full roster / production art | Beyond MVP | **DOC_ONLY** (explicit out of scope) |
| 28 | GAME-AA deterministic 2P vertical slice | Anime Track A | **IMPLEMENTED** (web/legacy slice claimed in PRD checkboxes) |
| 29 | GAME-AA rollback online multiplayer (Track B) | Full product | **STUB** |
| 30 | GAME-AA-011 ring gestures not mandatory without fairness proof | Competitive integrity | **DOC_ONLY** |
| 31 | Cross-game identical core rules / compatible saves / fair input (charter §8.1) | Platform rule | **DOC_ONLY** |
| 32 | DEV-STUDENT-002 all-day battery | Hardware Gate 2 | **DOC_ONLY** |
| 33 | DEV-STUDENT-007 hardware-backed security | Hardware | **DOC_ONLY** |
| 34 | DEV-STUDENT-010/011 dock + external displays | Hardware/OS | **STUB** (OS dock docs; no dock CAD SKU) |
| 35 | DEV-DSXL-002 dual-screen functional layouts | DS-XL UX | **DOC_ONLY** |
| 36 | DEV-HANDHELD-001 handheld+dockable compute role | Device role | **DOCUMENTED_DESIGN** |
| 37 | Manufacturing DFM / supply chain / provisioning (Gate 5 themes) | Preproduction | **DOC_ONLY** (packets exist) |
| 38 | Field pilot real users / ethics / NTN (Gate 4) | Field | **DOC_ONLY** |
| 39 | Carrier certification / fleet ops (Gate 7) | Deployment | **DOC_ONLY** |
| 40 | Gate 8 honest 6G / IMT-2030 migration mapping | Standards | **STUB** (standards snapshots + claim firewall) |
| 41 | SYS-MISSION-003 resilient multi-bearer connectivity | Connectivity | **DOC_ONLY/STUB** |
| 42 | SYS-MISSION-006 cross-form-factor application parity | Parity | **STUB** (device_ux roles docs in games) |
| 43 | SYS-MISSION-008 7GC as measurement environments | 7GC | **STUB** (digital twin + site matrices; not equal field ops) |
| 44 | OS-CONTINUITY-001…007 continuity transparency | Privacy UX | **DOC_ONLY** |
| 45 | Accessibility services across OS + games | Cross-cutting | **STUB** (req docs + gate4 protocols; not product-complete) |
| 46 | Secure application packaging / sandboxing | OS security | **DOC_ONLY/STUB** |
| 47 | Fleet management / observability | Gate 3 | **DOC_ONLY** |
| 48 | Repair procedures / FRU (G3_C7) | Support | **DOC_ONLY** (manual/matrix drafts) |
| 49 | Physical ring prototype authenticated input | Gate 1 evidence | **STUB** (digital fab + firmware; physical acceptance pending) |
| 50 | Product charter approval (Edmund) | Gate 0 blocker | **DOC_ONLY** — process pending human approval |

---

## 5. Explicitly not found (searched, do not invent)

| Expected artifact | Result |
|---|---|
| Standalone “Four-Game Master Requirements” / cross-game GDD file | **Not found** — content lives in charter §8 |
| Any file matching `*gdd*` / `*GDD*` except Beat Link `GAME_DESIGN_DOCUMENT.md` | **Not found** |
| Local clone of `EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon` | **Not in `repos/`** |
| Hardware `ADR-*.md` series for Student/DS-XL/Handheld/Rings/Dock | **Not found** |
| Dedicated Dock industrial-design CAD/BOM product folder | **Not found** (OS dock stack only) |
| Filled gunnchAI `docs/00`–`19` policy bodies | **Mostly stub redirects** |
| `gunnchOS3k` full OS requirements/GDD equivalent to device-os pack | **Not found** (quality/profile docs instead) |
| Attached binary “Gates 4–6 Acceptance-Grade Requirements” file referenced by `requirements/sources/README.md` | **Not copied into repo** (link/pointer only) |

---

## 6. Suggested next inventory passes (out of scope for this draft file’s claims)

1. Map each of 419 IDs → concrete code paths with evidence classes (prototype / nonphysical / physical).  
2. Clone or locate EdgeGesture and re-run ring requirement ownership.  
3. Reconcile research Gate docs vs product Gate 0–8 naming to avoid operator confusion.  
4. Promote Beat Link GDD + Anime PRD + Pedestrian MVP + Archive data policies into a single **Four-Game Master** index that cites charter §8 as authority (without rewriting requirements).

---

## 7. Audit metadata

- **Workspace root scanned:** `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos`
- **Excluded from “exists” claims:** `gate-worktrees/` duplicates (copies of field-kit branches), `node_modules/`, Unity `Library/`
- **Primary structured corpus count:** 419 requirements (`program/requirements/requirements.yaml` `count: 419`)
- **Draft path:** `gunnchos-7gc-ai-ran-field-kit/program/full_product/_source_inventory_draft.md`
