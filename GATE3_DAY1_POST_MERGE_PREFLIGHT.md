# GATE3_DAY1_POST_MERGE_PREFLIGHT

Generated after synchronizing merged default branches for Day 1 controlled pilot.

## Device

| Field | Value |
|---|---|
| adb | **DEVICE_AUTHORIZED** |
| Device | Pixel 6a |
| Android | 17 (API 37) |
| Serial | omitted from research artifacts |
| Host | macOS 26.5.2 |

## Repository SHAs (default branches, clean)

| Repo | Branch | HEAD | Expected merge / note |
|---|---|---|---|
| edge-io-measurement-node | main | `3b42a7c82a7a785cde85e0dbda9ed864f348d447` | PR #23 merge — MATCH |
| gunnchos-7gc-ai-ran-field-kit | master | `b7b3ca6426edaf1d3428b878f1bebd33ff0ee2a8` | PR #7 merge — MATCH |
| 7gc-digital-twin | main | `fcc9b11df3be2205efc501e724745b6947563be7` | clean |
| spectrumx-ai-ran-gary | main | `f7af6c7f7541360e07402f6927794116a1684d32` | clean |
| ntn-resilience-sim | main | `2403456d03d5eba6e4f56c0fd9e18e141ed2761a` | clean |

Manifest: `/tmp/gunnchos_gate3_day1_repo_manifest.json`

Field-kit dirty work from the prior pilot branch was stashed before sync
(`day1-preflight-preserve-*`) so master could fast-forward cleanly.

## Baseline checks

| Check | Result |
|---|---|
| `validate_gate1_thesis.py` | **GATE_1_PASS** |
| `make verify-repo-lock` | **FAIL** — `edge-io-measurement-node` lock still expects pre-merge `764192f…`; actual merged main is `3b42a7c…` |
| field-kit `pytest` | 74 passed, **1 failed** (`test_repo_lock_matches_current_checkouts` — same lock drift) |
| `make gate4-evaluation-ready` | **GATE4_EVALUATION_READY** |
| edge-io Python `pytest` | 18 passed |
| Android `./gradlew clean test assembleDebug` | **BUILD SUCCESSFUL** |

## Clean pilot APK (post-merge main)

| Field | Value |
|---|---|
| Path | `edge-io-measurement-node/clients/android/app/build/outputs/apk/debug/app-debug.apk` |
| SHA-256 | `c65c203c33793f8f64060a70d2cc318ba9ebcbc2a404f6c706a41ec349b89025` |
| Package | `org.gunnchos.edgeio.debug` |
| versionName | `0.4.1-gate3-pilot` |
| versionCode | 7 |
| GIT_COMMIT | `3b42a7c82a7a785cde85e0dbda9ed864f348d447` |
| GIT_DIRTY | **false** |
| Protocol | `gate3-pilot-v1` |
| Build timestamp | `2026-07-24T00:11:46Z` |

APK not committed. Not yet reinstalled in this Day 1 run (paused for design approval).

## Pilot coverage entering Day 1

**0 / 54**

Calibration and PILOT_REHEARSAL remain excluded.

## Gate status

- Gate 1: GATE_1_PASS
- Gate 2: GATE2_SYSTEM_PASS
- Release evidence: RELEASE_EVIDENCE_PENDING
- Gate 3: GATE3_PARTIAL_EVIDENCE
- Gate 4: GATE4_EVALUATION_READY

## Blocking items before Day 1 collection

1. **Human-approved pilot design placeholders are still unset** in the Day 1 master prompt:
   - `zone_a` / `zone_b` / `zone_c` location categories
   - `condition_1` / `condition_2`
   - `day_01` / `day_02` / `day_03` dates  
   **Day 1 assignments must not be generated until these are provided.**

2. **Repo-lock drift** after PR #23 merge: update `integration/repo-lock.json` expected edge-io commit to `3b42a7c…` (documentation/provenance fix; draft PR only if needed) so `verify-repo-lock` and provenance tests PASS on clean defaults.

## Stop / pause

Post-merge preflight complete enough to show merge commits and a clean APK identity.

**Paused before assignment generation** pending Edmund’s approved zones, network conditions, and dates.
