# Industry Resource Adoption Report

Updated: `2026-08-08T00:00:00Z`  
`PHYSICAL_EXECUTION_FREEZE = ACTIVE`

## Purpose

Score shortlist industry resources (0–5 criteria) and record ADOPT / ADAPT_INTERFACE / TEST_ONLY / REFERENCE_ONLY / DEFER / REJECT. No conference trophy shelf.

## Criteria

Higher better: requirement_alignment, technical_value, reproducibility, maintainer_health, portability, test_value, current_repo_fit.  
Lower better: vendor_lock_in_risk, license_product_risk, integration_cost.

## Decisions

| Resource | ID | Decision | License | Reason |
|----------|----|----------|---------|--------|
| NVIDIA Sionna | `nvidia_sionna` | **ADOPT** | Apache-2.0 | GPU-accelerated differentiable sim with CPU/fixture fallback for CI. |
| NYUSIM | `nyusim` | **ADOPT** | Academic/industrial free (vendor terms) | Complements Sionna for academic channel-model validation; not a duplicate engine. |
| 5G-LENA / ns-3 | `fiveg_lena_ns3` | **TEST_ONLY** | GPL-2.0 | GPL boundary — external process only; never link into product binaries. |
| OpenAirInterface / FlexRIC | `oai_flexric` | **TEST_ONLY** | OAI-CSSL | Research/test lab only; FRAND/commercial EP review before any product path. |
| O-RAN Software Community | `oran_sc` | **ADAPT_INTERFACE** | Apache-2.0 | O-RAN architecture alignment via interfaces, not mandatory runtime dependency. |
| Open5GS | `open5gs` | **TEST_ONLY** | AGPL-3.0 | AGPL — separately deployed lab component only. |
| CAMARA / GSMA Open Gateway APIs | `camara` | **ADAPT_INTERFACE** | Apache-2.0 (API specs; operator terms apply) | Optional connectivity insights; never REAL_OPERATOR without credentials. |
| OpenTelemetry | `opentelemetry` | **ADOPT** | Apache-2.0 | Backend-replaceable OTLP; local-first; no PII by default. |
| Grafana OSS | `grafana_oss` | **TEST_ONLY** | AGPL-3.0 | Standalone AGPL backend; never embed; OTel keeps backends replaceable. |
| Zephyr RTOS | `zephyr` | **ADOPT** | Apache-2.0 | Primary MCU candidate for nRF52840 ring with BLE + native_sim. |
| MCUboot | `mcuboot` | **ADOPT** | Apache-2.0 | Dev signing only; never store production private keys. |
| Tracy profiler | `tracy` | **ADAPT_INTERFACE** | BSD-3-Clause | Adopt where engine allows; else native profiler + OTel equivalents. |
| OpenXR | `openxr` | **ADAPT_INTERFACE** | Apache-2.0 (spec/registry) | Action/haptic abstraction; do not convert ordinary games to VR. |
| Vulkan | `vulkan` | **REFERENCE_ONLY** | Apache-2.0 (spec) | Capability target; no engine rewrite for Vulkan. |
| WebRTC | `webrtc` | **DEFER** | BSD-style (implementation-dependent) | Beat Link retains server-authoritative WS score/state; WebRTC not required for scoring. |
| Catalogue of Life / ChecklistBank | `catalogue_of_life` | **ADOPT** | CC-BY-4.0 (content unless indicated) | Living/extant taxonomic backbone with version provenance. |
| GBIF | `gbif` | **ADOPT** | Per-dataset (preserve citation) | Occurrence/distribution enrichment with per-record licensing. |
| Smithsonian Open Access | `smithsonian_oa` | **ADAPT_INTERFACE** | CC0 where marked; verify rights metadata | Open-access media only when rights metadata permits; never assume all CC0. |
| Godot Engine | `godot` | **ADOPT** | MIT | Keep where already used; do not rewrite Unity/web games to Godot. |

## Sources

- `program/industry_adoption/registry.yaml`
- `program/industry_adoption/scoring.schema.json`
- `program/industry_adoption/adopted_interfaces.yaml`
- `program/industry_adoption/rejected_or_deferred.yaml`

## Non-claims

- No REAL_OPERATOR CAMARA access without credentials.
- Tier-0 fixtures pass without GPU/external tools.
- Grafana OSS = TEST_ONLY standalone (AGPLv3); OTel backends remain replaceable.
