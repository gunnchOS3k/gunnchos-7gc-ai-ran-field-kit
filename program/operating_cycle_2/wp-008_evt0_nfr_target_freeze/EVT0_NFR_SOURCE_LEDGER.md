# EVT0 NFR Source Ledger (WP-008)

Generated: 2026-08-10T21:15:00Z  
Freeze: `EVT0_NFR_TARGET_REGISTRY_FROZEN=true` (implementer; verifier independent)

## Doctrine

- No fabricated competitor measurements (`competitor_score` always null here).
- Marketing peaks are not sustained requirements without justification.
- WP-010 instrument matrices were **not landed** at implementer time → instruments marked `TBD_WP010`.
- Preference / human quality → E6 only; not substituted with invented scores.

## Evidence hierarchy applied

1. Safety/regulatory — IEC 62368-1 TS1 sustained touch ~48°C (class); product uses accepted `skin_c_max=45`.
2. MLP — school day, dock, offline, local AI, Rings safety, update/recovery.
3. Accepted hardware — profiles `skin_c_max`, `max_charge_w=65`, `wifi:6e_minimum`; WP-002 storage reserves; `os_thermal_policy.yaml throttle_c=85`; Ring `UNCERTAIN_CONFIDENCE_THRESHOLD=0.85`.
4. Competitor **class/outcome** (not scores) — education Chromebook school-day class; Steam Deck OLED published battery condition class (30FPS/50% brightness); Valve resume feature class.
5. Usability/engineering budgets — latency/boot/resume provisional numbers with LOW/MEDIUM confidence.
6. Explicit provisional / TBD — Fast/Pro AI, power watts, Ring mm drift, Wi-Fi Mbps, microSD write, fan noise.

## Primary internal sources

| Source | Path / ref | Date |
|---|---|---|
| WP-008 packet | `gunnchOS3k_Operating_Cycle_2 copy/WP-008_EVT_NFR_TARGET_FREEZE.md` | 2026-08-10 |
| NFR seed registry | `program/operating_model/08_NONFUNCTIONAL_COMPETITIVE/NONFUNCTIONAL_REQUIREMENTS.json` | repo main |
| Competitive strategy | `.../COMPETITIVE_STRATEGY_MATRIX.md` | repo main |
| Golden Journeys | `program/operating_model/02_QUALITY_USERS/GOLDEN_JOURNEYS.json` | repo main |
| MLP | `gunnchOS3k_Operating_Model copy/02_QUALITY_USERS/MINIMUM_LOVABLE_PRODUCT.md` | 2026-08-10 |
| Risk register | `.../06_RISK_UNKNOWN_SUPPLY/RISK_REGISTER.json` | repo main |
| Hardware profiles | `gunnchos-hardware-industrial-design/results/contracts/*_hardware_profile.json` | accepted main |
| Thermal policy | `.../thermal/*/os_thermal_policy.yaml` | accepted |
| Storage policy WP-002 | `.../npi/phase_xv/handheld_storage_headroom/HANDHELD_STORAGE_POLICY.md` | VP-002 |
| Factory boot placeholder | `.../manufacturing/student_14_5/factory_test/limits_schema.json` | note: not lab-calibrated |
| Ring confidence gate | `gunnchos-device-os/.../silent_destructive_uncertain_gestures.py` | accepted main |
| Ring drift heuristic | `edge-io-measurement-node/firmware/ring_calibration/fallback_policy.yaml` | physical pending |
| Competitor readiness matrix | `gunnchos-device-os/quality/golden_journeys/COMPETITOR_READINESS_GAP_MATRIX.json` | WP-003R.1 |
| Equipment list (bridge) | `program/physical/MASTER_TEST_EQUIPMENT_LIST.csv` | prep only |
| WP-010 packet | `WP-010_EVT0_FIXTURE_INSTRUMENT_READINESS.md` | instruments not yet in-repo |

## External / class sources (dated; not competitor_score)

| Claim used | Source | Date | How used |
|---|---|---|---|
| Steam Deck OLED battery 3–12h; conditions 30FPS/50% brightness/50% volume | https://www.steamdeck.com/en/tech/oled | retrieved 2026-08-10 (Valve OLED era 2023-11) | Class outcome for Handheld MUST_MATCH; **target 3h**, not 12h peak |
| Steam Deck OLED 20–80% charge “as little as 45 min”; resume improved ~30% | https://www.steamdeck.com/en/oled | 2023-11 / retrieved 2026-08-10 | Stretch class for charge; resume feature class only |
| Education Chromebook “school day” / PLT multi-hour claims | Dell Chromebook 3100 EDU spec (PLT up to 13h25); Samsung Galaxy Chromebook Go (12h PLT) | datasheets retrieved 2026-08-10 | Class for Student day; **PLT peaks not used as threshold** |
| IEC 62368-1 TS1 sustained touch ~48°C metal/plastic | IEC 62368-1 Table 38 class; UL touch-temp tech brief | standard class / UL brief | Regulatory outer bound; product threshold 45°C from hardware |

## Confidence legend

- **HIGH** — accepted hardware/policy/safety property or already-frozen zero-loss requirements.
- **MEDIUM** — MLP + dated class outcome with conservative interpretation.
- **LOW** — provisional engineering budget pending EVT characterization or WP-010 fixtures.

## Change control

After freeze, altering threshold/target/stretch requires a change record citing new evidence. Physical results must not rewrite targets retroactively.
