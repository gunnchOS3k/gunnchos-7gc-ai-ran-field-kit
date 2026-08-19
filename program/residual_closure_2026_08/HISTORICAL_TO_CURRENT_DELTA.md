# HISTORICAL_TO_CURRENT_DELTA

Generated: `2026-08-19T03:15:52Z`
Audit: `GUNNCHOS_ECOSYSTEM_RESIDUAL_DIGITAL_CLOSURE_2026_08_19`
Policy: Cursor never merges. Never mix preview PR SHAs with accepted-main.

## Historical map used

Spine `program/docs` was **absent** (spine `program/*.md` are 1-byte placeholders). The August 15/16 completion analysis that actually exists is:

- Field-kit `program/digital_ecosystem_baseline_v1/` (`GUNNCHOS_DIGITAL_ECOSYSTEM_BASELINE_V1`, generated `2026-08-16T16:15:56Z`)
- That snapshot already included the August 15 merges: device-os #116, gunnchAI #36/#38, WAIKE #48, field-kit R6G #80

**This file treats that baseline as HISTORICAL_GAP_MAP only.** It does not execute the August 16 Stream A/B/C PR sequence. Those packets later landed on accepted-main.

The 569-atom `COMPLETION_LEDGER.json` (PASS=35 / DIGITAL_OPEN=483 / 6.76%) is **not** re-scored here. Using that percentage as current truth would be false. Named product streams below are classified from live `origin/main` + `gh`.

## Accepted-main SHA movement (baseline → now)

| Repo | Baseline V1 SHA | Current origin/main | Tip merge |
|---|---|---|---|
| gunnchos-device-os | `a1e11ef` (#116) | `d5c2d17` | #121 |
| gunnchAI3k | `c429750` (#36) | `d357846` | **#43 MERGED** |
| waike-research-ops | `7a0d4fe` (#48) | `4917443` | #52 |
| gunnchos-7gc-ai-ran-field-kit | `d1b330a` (#80) | `8464f17` | #87 |
| gunnchos-hardware-industrial-design | `08b4d22` (#64) | `9ee0ef2` | #67 |
| edge-io-measurement-node | `3a16ba0` | `af57fbd` | #38 |
| anime-aggressors | `9770674` | `a7d1153` | #79 |
| pedestrian-pursuit | `80ca8ee` | `8f513c2` | #20 |
| archive-of-life-artifact-world | `74f5761` | `bf47908` | #33 |
| beatlink-party | `4fc8fe0` | `6e8d1a0` | #23 |
| 7gc-digital-twin | `ce09f2f` | `4cd7016` | #30 |
| spectrumx-ai-ran-gary | `8f0df4c` | `cef3900` | #101 |
| ntn-resilience-sim | `cd49b66` | `9165209` | #27 |
| readygary-6g-beam-selection | `525405c` | `0e2a791` | **#26 MERGED** |
| gunnchos-gpu-nr-baseband-platform | `64909ee` | `3931f51` | #3 |
| gunnchos-emergent-service-intent-protocols | `9b3fec9` | `088c5e8` | #3 |
| gunnchos-research-portal | *(not in V1 SHA lock)* | `7842ff2` | #8 |

## Prompt-stale “open drafts” that are now accepted-main

Do **not** treat these as PREVIEW anymore:

| Item | Prompt said | GitHub truth 2026-08-19 |
|---|---|---|
| gunnchAI #43 | OPEN DRAFT / do not ingest into accepted-main | **MERGED** `d357846` — it **is** accepted-main |
| ReadyGary #26 Sub-6/dual-band | PREVIEW while unmerged | **MERGED** `0e2a791` — it **is** accepted-main |
| portal #8 | possibly open | **MERGED** `7842ff2` |
| Pixel evidence #79/#23/#38/#20/#33 | possibly open | **MERGED** |
| spectrumx #101 | possibly open | **MERGED** |

device-os #103 remains OPEN draft CONFLICTING. Do not merge.

## Named historical gap classification

Classification enum: `CLOSED_BY_ACCEPTED_MAIN | PARTIALLY_CLOSED | STILL_DIGITAL_OPEN | HUMAN_PENDING | PHYSICAL_PENDING | EXTERNAL_PENDING | STANDARD_PENDING | SUPERSEDED`

### Product streams (August 16 proposed packets)

| Historical gap | Classification | Evidence |
|---|---|---|
| Stream A PKT-001/002/003 device-os middleware/emulation/creation | CLOSED_BY_ACCEPTED_MAIN | device-os #117 #118 #119 #120 merged; tip #121 |
| Stream A field-kit BASELINE_V1 control plane | CLOSED_BY_ACCEPTED_MAIN | field-kit #81 merged (then superseded by later C packets / #87 tip) |
| Stream B WAIKE live taxonomy + COMM_PD + DATA_DASHBOARDS | CLOSED_BY_ACCEPTED_MAIN | WAIKE #49 #50 #51 then #52 |
| Stream B gunnchAI companion/tools/mastery packets | CLOSED_BY_ACCEPTED_MAIN | gunnchAI #39 #40 #41 #42 then **#43** |
| Stream B game playtest/polish packets | CLOSED_BY_ACCEPTED_MAIN | anime #77/#78/#79; pedestrian #18/#19/#20; archive #31/#32/#33; beatlink #22/#23 |
| Stream C hardware digital exhaustion | CLOSED_BY_ACCEPTED_MAIN | hardware #65 #66 #67. Do not regenerate handoff packets. |
| Stream C R6G ladder depth + NVIDIA/Oulu | PARTIALLY_CLOSED | field-kit #82 #84 #86 #87 merged. Independent/physical/OTA still pending. Do not restart #80. |
| Emergent publication science #2 | CLOSED_BY_ACCEPTED_MAIN | emergent #2 then supervisor-ready #3 merged |
| Supervisor-ready 16-repo portfolio | CLOSED_BY_ACCEPTED_MAIN | device-os #121, hardware #67, WAIKE #52, gunnchAI #42, games, ntn #27, 7gc #30, spectrumx #100, ReadyGary #24/#25, portal #7, gpu-nr #3, emergent #3, then Pixel/portal refresh PRs |

### WAIKE 18-track DIGITAL_RC

| Track | Classification | Note |
|---|---|---|
| SOFTWARE_BUILDER, NETWORKING via COMPUTER_NETWORKING, CYBER via CYBERSECURITY, DATA_DASHBOARDS, AI_ML_EDGE, WIRELESS_6G, PM_AGILE_LSS, GAME_DEV_INTERACTIVE, CLOUD_DEVOPS, COMM_PD_ETHICS, ROBOTICS_CONTROL, HARDWARE_ENGINEERING, DATA_VIZ_BI, GENERAL_IT | CLOSED_BY_ACCEPTED_MAIN | 14 `curriculum/digital_rc/*` packages on `4917443` |
| DIGITAL_CONFIDENCE, IT_SUPPORT_HARDWARE | CLOSED_BY_ACCEPTED_MAIN | Mapped into GENERAL_IT; no standalone package by design |
| NETWORKING_INFRA / CYBER_SOC ledger rows “Not authored” | PARTIALLY_CLOSED | Packages exist as COMPUTER_NETWORKING / CYBERSECURITY; B-PKT-003 ledger (`2026-08-16`) is stale vs course IDs |
| EMBEDDED_PROTOTYPING | STILL_DIGITAL_OPEN | No `curriculum/digital_rc` package. Assignment bodies exist under `edge_ai_embedded`. Digitally authorable. |
| GUNNCHOS_PRODUCT_LAB | STILL_DIGITAL_OPEN | Assignment bodies exist; `device_os_curriculum_pr=false`; no DIGITAL_RC package |
| SEVEN_GC_APPRENTICESHIP | STILL_DIGITAL_OPEN | Research overlay, not a 19th invented course. Apprenticeship tracks exist; not COURSE_DIGITAL_RC |
| REAL_STUDENT_E6 / REAL_TEACHER_E6 / LEARNING_EFFECTIVENESS / HUMAN_E6 | HUMAN_PENDING | Must remain false |

### Games

| Historical gap | Classification | Note |
|---|---|---|
| GAME-RC-003/004 digital launch campaigns | CLOSED_BY_ACCEPTED_MAIN | Merged before baseline; later supervisor-ready + Pixel evidence |
| Pixel 6a install+launch | CLOSED_BY_ACCEPTED_MAIN | anime #79, beatlink #23, pedestrian #20, archive #33. CI on main = success |
| Fun / balance / feel / onboarding / party / visual polish | HUMAN_PENDING | Not automatable product work |
| Acoustic physical validation | PHYSICAL_PENDING | |
| Archive scientific data rights | EXTERNAL_PENDING | |
| anime Unity #51/#52 vs Godot main | SUPERSEDED | Destructive ambiguity. Godot is accepted-main path. Do not auto-start Unity. Owner path decision only |
| README WP-012 contract drafts (anime #71, pedestrian #13, archive #26, beatlink #17) | SUPERSEDED | Historical docs; not current product blockers |

### device-os #103

| Historical gap | Classification | Note |
|---|---|---|
| Merge #103 onto current main | SUPERSEDED | CONFLICTING vs post-#116/#121 main. Do not merge. |
| Unique #103 capabilities vs current main | STILL_DIGITAL_OPEN | 32 commits / 100 files on head `071f9b28`. Full unique-commit classification + port **not completed in Phase 0**. |
| Re-land #103 screenshots/logs as current evidence | SUPERSEDED | Stale evidence. Forbidden. |

### device-os × gunnchAI contract

| Historical gap | Classification | Note |
|---|---|---|
| Do not ingest unmerged gunnchAI #43 | SUPERSEDED | #43 is merged. Accepted-main pairing is device-os `d5c2d17` × gunnchAI `d357846`. |
| Versioned compatibility contract / no hidden coupling | PARTIALLY_CLOSED | Supervisor-ready paths exist. Explicit versioned contract vs gunnchAI #43 tip still worth a narrow check — not a new ingest of a draft SHA. |

### Hardware

| Historical gap | Classification | Note |
|---|---|---|
| HW-FW-RC-001 digital packages | CLOSED_BY_ACCEPTED_MAIN | #64 |
| C-PKT hardware digital + EVT digital readiness | CLOSED_BY_ACCEPTED_MAIN | #65 #66 |
| Supervisor-ready manufacturing packet | CLOSED_BY_ACCEPTED_MAIN | #67. `artifacts/supervisor_ready_eda/` present. Do not repeat handoff packets. |
| Student 14.5 DIGITAL_RELEASE | EXTERNAL_PENDING | `DIGITAL_RELEASE_BLOCKED_EXTERNAL_DATA` — `EXT-COM-HPC-400PIN` PICMG/ADLINK 400-pin map |
| DS-XL DIGITAL_RELEASE | EXTERNAL_PENDING | Same COM-HPC map + `EXT-DSXL-DUAL-EDP` |
| Rings DIGITAL_RELEASE | CLOSED_BY_ACCEPTED_MAIN | `DIGITAL_RELEASE_READY` on main. `DIGITAL_FABRICATION_PASS=false` |
| Handheld DIGITAL_RELEASE | CLOSED_BY_ACCEPTED_MAIN | `DIGITAL_RELEASE_READY`. 461 ERC warnings classified in #67 disposition (not re-run here). `DIGITAL_FABRICATION_PASS=false` |
| Dock token | EXTERNAL_PENDING | Token not earned: `EXT-JHL8440-BALLMAP`, `EXT-JHL9040R-BALLMAP` |
| DIGITAL_FABRICATION_PASS | PHYSICAL_PENDING | False on all SKUs. No fabricated physical validation. |
| RFQ / FCC / CE / USB-IF / chamber / vendor | EXTERNAL_PENDING + PHYSICAL_PENDING | |

### R6G / NVIDIA / manuscripts

| Historical gap | Classification | Note |
|---|---|---|
| R6G-PORTFOLIO-ADOPTION-002 #80 | CLOSED_BY_ACCEPTED_MAIN | Do not restart |
| R6G-006/007 digital contract depth #82 | CLOSED_BY_ACCEPTED_MAIN | MODELED_CONTRACT_ONLY |
| NVIDIA × Oulu digital reproduction | PARTIALLY_CLOSED | #84 #86 #87 fail-closed CPU analytical bridge. Aerial/AODT/Sionna UNAVAILABLE |
| R6G_DIGITAL_REPLICATION_PASS / multi-seed / independent verifier | STILL_DIGITAL_OPEN | Tokens false on `8464f17`. Only remaining local digital replication — do not flip PHYSICAL/OTA/CARRIER/STANDARDIZED from software |
| DIGITAL_REPRODUCTION_MATCHED to published physical | PHYSICAL_PENDING | Structural only |
| DOI/PDF pins | EXTERNAL_PENDING | |
| STANDARDIZED_6G / CARRIER_ACCEPTED / OTA | STANDARD_PENDING / EXTERNAL_PENDING / PHYSICAL_PENDING | Remain false |
| ReadyGary Sub-6/dual-band Paper II duplicate | SUPERSEDED | #26 merged; do not duplicate Paper II SoT. Exactly three dissertation papers. |
| Conference SUBMITTED/ACCEPTED | HUMAN_PENDING | Portal snapshot: not SUBMITTED; not ACCEPTED |

### Portal

| Historical gap | Classification | Note |
|---|---|---|
| Supervisor-ready portal #7 | CLOSED_BY_ACCEPTED_MAIN | |
| Portal #8 snapshot refresh after Pixel/GPU-NR/emergent | CLOSED_BY_ACCEPTED_MAIN | Landed `7842ff2` |
| Snapshot still mixing PR SHAs and omitting later accepted-main (#43, #26, current tips) | STILL_DIGITAL_OPEN | Refresh **last**, after other residual digital work. Distinguish ACCEPTED_MAIN \| PREVIEW_DRAFT \| PHYSICAL_PENDING \| HUMAN_PENDING \| EXTERNAL_PENDING |

## Honesty limits

- Phase 0 did **not** re-verify all 569 ledger atoms.
- Phase 0 did **not** port device-os #103 unique commits.
- Phase 0 did **not** author remaining WAIKE DIGITAL_RC packages.
- Local clones for device-os / archive / pedestrian may be dirty; SHAs above are `origin/main` only.
- Field-kit working copy is on already-merged branch `stream/nvidia-6g-phase0-mac-setup`; this residual packet is branched from `origin/main` `8464f17`.
