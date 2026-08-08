# Continuation V — Claim Integrity Audit

Updated: 2026-08-08T20:16:48Z

Doctrine: no attachment to prior tokens. Revoke if evidence contradicts the claim.
Allowed validity: `VALID` | `VALID_WITH_EXPLICIT_SCOPE` | `PREMATURE_REVOKE` | `SUPERSEDED`.

## Anime Beta/RC contradiction (known)

`content/missing_assets.json` lists launch art assets with `blocks_token: true` while
`ANIME_BETA_CONTENT_COMPLETE_DIGITAL` / `ANIME_DIGITAL_RC_READY` are claimed on accepted main.
Cont V marks both **PREMATURE_REVOKE**. Field-kit `scripts/validate_game_release_claims.py`
rejects Beta/RC claims when any `blocks_token=true` asset remains.

## Token table

| Token | Repo | Validity | Action |
|-------|------|----------|--------|
| `ANIME_BETA_CONTENT_COMPLETE_DIGITAL` | anime-aggressors | `PREMATURE_REVOKE` | Revoke until blocks_token=true assets resolved or Beta rule explicitly re-scoped |
| `ANIME_DIGITAL_RC_READY` | anime-aggressors | `PREMATURE_REVOKE` | Revoke until Beta content token is valid under claim firewall |
| `PEDESTRIAN_BETA_CONTENT_COMPLETE_DIGITAL` | pedestrian-pursuit | `VALID_WITH_EXPLICIT_SCOPE` | Keep scoped to digital systems; do not claim visual/store Beta |
| `PEDESTRIAN_DIGITAL_RC_READY` | pedestrian-pursuit | `VALID_WITH_EXPLICIT_SCOPE` | Keep PARTIAL; do not promote to READY until packaging+AI matrix close |
| `ARCHIVE_BETA_CONTENT_COMPLETE_DIGITAL` | archive-of-life-artifact-world | `VALID_WITH_EXPLICIT_SCOPE` | Retain only if frozen launch Tier E/F set complete; else revoke |
| `ARCHIVE_DIGITAL_RC_READY` | archive-of-life-artifact-world | `VALID_WITH_EXPLICIT_SCOPE` | Keep digital-RC scope; no live global ingest claim |
| `BEATLINK_BETA_CONTENT_COMPLETE_DIGITAL` | beatlink-party | `VALID_WITH_EXPLICIT_SCOPE` | Scope to current DEV/sim depth OR revoke after Cont V Redis/mic closure decision |
| `BEATLINK_DIGITAL_RC_READY` | beatlink-party | `VALID_WITH_EXPLICIT_SCOPE` | Keep DEV signing / digital packaging scope only |
| `GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS` | gunnchos-device-os | `VALID_WITH_EXPLICIT_SCOPE` | Keep narrow boot token; forbid FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE |
| `FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE` | gunnchos-device-os | `PREMATURE_REVOKE` | Ensure never claimed; Cont V stub elimination wave |
| `GUNNCHAI_REAL_LOCAL_INFERENCE_PASS` | gunnchAI3k | `VALID` | Keep; do not equate to FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE |
| `FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE` | gunnchAI3k | `PREMATURE_REVOKE` | Forbidden until Cont V AI productization closes |
| `HARDWARE_DESIGN_RELEASE_CANDIDATE` | gunnchos-hardware-industrial-design | `VALID_WITH_EXPLICIT_SCOPE` | Keep CANDIDATE; FULL_HARDWARE_DESIGN_RELEASE_COMPLETE forbidden |
| `FULL_HARDWARE_DESIGN_RELEASE_COMPLETE` | gunnchos-hardware-industrial-design | `PREMATURE_REVOKE` | Forbidden until KiCad CLI + package completeness |
| `RING_ZEPHYR_WEST_BUILD_PASS` | edge-io-measurement-node | `VALID` | Keep; no physical flash claim |

## Per-token detail

### `ANIME_BETA_CONTENT_COMPLETE_DIGITAL`

- **repo:** `anime-aggressors`
- **claiming artifact:** `docs/ANIME_BETA_CONTENT_STATUS.md`
- **accepted_main_sha:** `1555ba3988b7026e418a0199cf5d10e1cfc384a8`
- **validity:** `PREMATURE_REVOKE`
- **action:** Revoke until blocks_token=true assets resolved or Beta rule explicitly re-scoped
- **requirements:**
  - Beta launch content complete under digital Beta rule
- **blocking artifacts:**
  - `content/missing_assets.json`
  - `builds/digital-rc/content/missing_assets.json`
- **contradictions:**
  - 13 assets with status=REQUIRES_ART_PRODUCTION and blocks_token=true (7 fighter model GLBs + 6 stage art) while token claimed YES

### `ANIME_DIGITAL_RC_READY`

- **repo:** `anime-aggressors`
- **claiming artifact:** `playtest-evidence/digital_rc_validation.json`
- **accepted_main_sha:** `1555ba3988b7026e418a0199cf5d10e1cfc384a8`
- **validity:** `PREMATURE_REVOKE`
- **action:** Revoke until Beta content token is valid under claim firewall
- **requirements:**
  - Beta content complete + RC runner
- **blocking artifacts:**
  - `content/missing_assets.json`
  - `docs/ANIME_BETA_CONTENT_STATUS.md`
- **contradictions:**
  - RC token_earned=true depends on Beta content complete, which is PREMATURE_REVOKE

### `PEDESTRIAN_BETA_CONTENT_COMPLETE_DIGITAL`

- **repo:** `pedestrian-pursuit`
- **claiming artifact:** `docs/PEDESTRIAN_BETA_DIGITAL_RC_STATUS.md`
- **accepted_main_sha:** `c8db661d6bf057c6c487586f378362005413bc1f`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Keep scoped to digital systems; do not claim visual/store Beta
- **requirements:**
  - Beta digital systems / catalog / modes
- **blocking artifacts:**
  - `art REQUIRES_ART_PRODUCTION`
- **contradictions:** none recorded

### `PEDESTRIAN_DIGITAL_RC_READY`

- **repo:** `pedestrian-pursuit`
- **claiming artifact:** `docs/PEDESTRIAN_BETA_DIGITAL_RC_STATUS.md`
- **accepted_main_sha:** `c8db661d6bf057c6c487586f378362005413bc1f`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Keep PARTIAL; do not promote to READY until packaging+AI matrix close
- **requirements:**
  - Digital RC packaging
- **blocking artifacts:**
  - `store/device RC`
  - `competitive AI matrix`
- **contradictions:**
  - Documented PARTIAL

### `ARCHIVE_BETA_CONTENT_COMPLETE_DIGITAL`

- **repo:** `archive-of-life-artifact-world`
- **claiming artifact:** `docs/BETA_RC_STATUS.md`
- **accepted_main_sha:** `5cb81fbd8de592a38e7e642185ef5e41e81aad98`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Retain only if frozen launch Tier E/F set complete; else revoke
- **requirements:**
  - Frozen launch Tier E/F complete
- **blocking artifacts:**
  - `live global ingest`
  - `IUCN token`
  - `Tier E/F audit`
- **contradictions:**
  - Global complete explicitly false; Cont V must audit Tier E/F

### `ARCHIVE_DIGITAL_RC_READY`

- **repo:** `archive-of-life-artifact-world`
- **claiming artifact:** `public/data/status/digital_rc_report.json`
- **accepted_main_sha:** `5cb81fbd8de592a38e7e642185ef5e41e81aad98`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Keep digital-RC scope; no live global ingest claim
- **requirements:**
  - Package + provenance + offline packs + Beta digital
- **blocking artifacts:**
  - `live operator ingest credentials`
- **contradictions:** none recorded

### `BEATLINK_BETA_CONTENT_COMPLETE_DIGITAL`

- **repo:** `beatlink-party`
- **claiming artifact:** `docs/BETA_RC_TOKENS.json`
- **accepted_main_sha:** `dd9f32dbc550e28138d7764813ad07256bfffd6b`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Scope to current DEV/sim depth OR revoke after Cont V Redis/mic closure decision
- **requirements:**
  - Launch digital functionality complete
- **blocking artifacts:**
  - `in_memory_rooms_no_redis`
  - `no_live_getUserMedia_pitch`
  - `no_licensed_lyrics_or_platform_sdks`
- **contradictions:**
  - Token true while Cont V prompt lists digitally executable Redis/mic gaps

### `BEATLINK_DIGITAL_RC_READY`

- **repo:** `beatlink-party`
- **claiming artifact:** `docs/digital-rc/ready.json`
- **accepted_main_sha:** `dd9f32dbc550e28138d7764813ad07256bfffd6b`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Keep DEV signing / digital packaging scope only
- **requirements:**
  - Digital RC packaging
- **blocking artifacts:**
  - `store/HSM/physical RC`
- **contradictions:** none recorded

### `GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS`

- **repo:** `gunnchos-device-os`
- **claiming artifact:** `docs/full_product/BOOTABLE_REFERENCE_IMAGE.md`
- **accepted_main_sha:** `dee336a344bbc3ac730ed2cfd25a5f1d1e1af49f`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Keep narrow boot token; forbid FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE
- **requirements:**
  - QEMU aarch64 boot evidence
- **blocking artifacts:**
  - `17 service stubs in image`
- **contradictions:** none recorded

### `FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE`

- **repo:** `gunnchos-device-os`
- **claiming artifact:** `(forbidden while stubs remain)`
- **accepted_main_sha:** `dee336a344bbc3ac730ed2cfd25a5f1d1e1af49f`
- **validity:** `PREMATURE_REVOKE`
- **action:** Ensure never claimed; Cont V stub elimination wave
- **requirements:**
  - All digitally executable platform services real
- **blocking artifacts:**
  - `17 service stubs`
- **contradictions:**
  - Would contradict stub inventory

### `GUNNCHAI_REAL_LOCAL_INFERENCE_PASS`

- **repo:** `gunnchAI3k`
- **claiming artifact:** `evidence/system-layer/REAL_INFERENCE_BENCH.json`
- **accepted_main_sha:** `6f98ab8b08851ad4e0ac8785bb409c248519b2b7`
- **validity:** `VALID`
- **action:** Keep; do not equate to FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE
- **requirements:**
  - Reproducible local llama.cpp inference bench
- **blocking artifacts:**
- **contradictions:** none recorded

### `FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE`

- **repo:** `gunnchAI3k`
- **claiming artifact:** `(not earned)`
- **accepted_main_sha:** `6f98ab8b08851ad4e0ac8785bb409c248519b2b7`
- **validity:** `PREMATURE_REVOKE`
- **action:** Forbidden until Cont V AI productization closes
- **requirements:**
  - Callable capability service + governance + RAG + evals
- **blocking artifacts:**
  - `SCHEMA_ONLY AI capability nodes`
- **contradictions:** none recorded

### `HARDWARE_DESIGN_RELEASE_CANDIDATE`

- **repo:** `gunnchos-hardware-industrial-design`
- **claiming artifact:** `docs/full_product_family/HARDWARE_DESIGN_RELEASE_STATUS.md`
- **accepted_main_sha:** `7e1658e63052e7baa2e9f4ab58113a91e4165c72`
- **validity:** `VALID_WITH_EXPLICIT_SCOPE`
- **action:** Keep CANDIDATE; FULL_HARDWARE_DESIGN_RELEASE_COMPLETE forbidden
- **requirements:**
  - Exact-MPN candidate packages for five products
- **blocking artifacts:**
  - `KiCad CLI EDMUND_ACTION_REQUIRED`
- **contradictions:** none recorded

### `FULL_HARDWARE_DESIGN_RELEASE_COMPLETE`

- **repo:** `gunnchos-hardware-industrial-design`
- **claiming artifact:** `(not claimed)`
- **accepted_main_sha:** `7e1658e63052e7baa2e9f4ab58113a91e4165c72`
- **validity:** `PREMATURE_REVOKE`
- **action:** Forbidden until KiCad CLI + package completeness
- **requirements:**
  - ERC/DRC/mfg export for all five
- **blocking artifacts:**
  - `EB-KICAD-ADMIN`
- **contradictions:** none recorded

### `RING_ZEPHYR_WEST_BUILD_PASS`

- **repo:** `edge-io-measurement-node`
- **claiming artifact:** `program/full_product/evidence_registry.yaml`
- **accepted_main_sha:** `fc617e831916362e77aa157d77d458e935dc4cfa`
- **validity:** `VALID`
- **action:** Keep; no physical flash claim
- **requirements:**
  - Zephyr west digital build
- **blocking artifacts:**
- **contradictions:** none recorded

## Machine-readable

- `program/full_product/continuation_v/claim_integrity_audit.yaml`
- Game claim firewall: `scripts/validate_game_release_claims.py`
