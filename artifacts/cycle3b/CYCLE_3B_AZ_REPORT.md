# Cycle 3B A–Z Report — INDEPENDENT FAIL WITH DEMOTIONS

Recorded: 2026-08-11T22:43:39Z
Cursor never merges. Profile README freeze ACTIVE. Generic README program PAUSED. WP-001 DO_NOT_START.

## Verdict
**INDEPENDENT_FAIL** on device-os #103 tip `769d898`. Implementer LIVE+DSXL+RING+FOUR_GAME+master claims demoted. ECO-010 1800s duration PASS retained (does not unlock master). Physical VF4/5/6 still PHYSICAL_PENDING.

## Token board
| Token | Status | Evidence |
|---|---|---|
| LIVE_GUNNCHOS_VISUAL_PASS | **false (demoted)** | guest FB fail; shell_app blank/identical; host_fb uncommitted — `artifacts/wp011r/visual/LIVE_VISUAL_EVIDENCE.json` |
| DSXL_DUAL_COMPOSITOR_UX_PASS | **false (demoted)** | GUEST_DUAL only; no compositor_ux_gate — `artifacts/wp011r/dsxl/DSXL_COMPOSITOR_UX_EVIDENCE.json` |
| RING_TO_REAL_APP_STATE_MUTATION_PASS | **false (demoted)** | uinput→mousepad ≠ Ring→LibreOffice/browser/game — `artifacts/wp011r/ring/RING_APP_MUTATION_EVIDENCE.json` |
| FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS | **false (demoted)** | Pedestrian = Chromium web + lab probe; Godot input/save open — `artifacts/wp011r/games/four_games_in_guest.json` |
| ECO010_SOAK_PASS | **true** | 1800.05s not shortened/dry; inject/recover 10/10 — `artifacts/wp011r/ECO010_SOAK.json` (qemu=null / flat rss caveat) |
| GUEST_DUAL_OUTPUT_PASS | **true** | guest_drm dual connectors |
| Master digital complete | **false** | independent mean 5.67 — `artifacts/wp011r/DEVICE_LAB_SCORE_INDEPENDENT.json` |

## Streams
### WP-011R — https://github.com/gunnchOS3k/gunnchos-device-os/pull/103 (DRAFT) — do not merge yet
### WP-013 — https://github.com/gunnchOS3k/gunnchos-device-os/pull/104 (DRAFT) tip `41a51f6` — exit tokens digital-only; PRODUCTION_RELEASE_CLAIMED=false
### Aggregation — field-kit #71 DRAFT

## Rejected false positives (applied)
- Chromium in-tree web / lab probe as Pedestrian Godot production
- DRM / wl_output count as DSXL compositor UX
- uinput mousepad as Ring→app mutation
- LIVE with failed guest FB + uncommitted host screendumps
- Inflated master complete

## Remaining blockers
1. FOUR_GAME Godot Pedestrian input/save in-guest
2. LIVE guest framebuffer + committed input-visible captures
3. DSXL compositor_ux_gate full path
4. Ring→LibreOffice/browser/game mutation
5. Physical VF4/5/6
6. WP-001 still DO_NOT_START

## Edmund merge order
**Do not merge #103 yet.**
1. Re-earn demoted WP-011R tokens on #103 (DRAFT)
2. #104 digital-only when accepted (never assert production release)
3. Game DRAFTs when accepted
4. field-kit #71 last
5. Never profile README; never start WP-001
