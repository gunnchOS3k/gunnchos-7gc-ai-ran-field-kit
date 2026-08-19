# device-os #103 supersession note (owner)

**Do not merge. Do not close automatically.** This is a classification record for Edmund.

- URL: https://github.com/gunnchOS3k/gunnchos-device-os/pull/103
- State: OPEN draft, `CONFLICTING`
- Head: `071f9b28b2cccd0549885e5f8427af4db3c162c5` (32 commits / 100 files vs merge-base `daf8e540`)
- Accepted-main compared: `d5c2d179ae21efe5191b7d35a2080878112f18e4` (#121, 2026-08-18)
- Compared: `origin/main...origin/pr-103` after fetch of `pull/103/head`. Dirty local device-os clone was not checked out.

## Classification of unique #103 capabilities

| Capability | Class | Why |
|---|---|---|
| Interactive Development Guest tree (`os_build/device_lab_interactive_guest/**`, guest agent, weston, provisioners) | ALREADY_PORTED | Same paths exist on current main; Stream A / WP-011R.2 evolved them further |
| `interactive_guest_proofs.py` LIVE / DSXL / RING earn paths | ALREADY_PORTED | Present on main; main is larger (diff vs #103 would **delete** 767 lines) |
| Dual virtio-gpu `device_del gpu1` DSXL disconnect | ALREADY_PORTED | Main already implements `dual_virtio_gpu_device_del_add` with honest FAIL → reboot reconfig |
| Ring browser `lab_browser.html` click-collector | OBSOLETE_ARCHITECTURE | Main **forbids** this collector (`lab_browser_collector_forbidden: true`); requires real Chromium document autosave (`RingMemo.txt`) |
| Guest-agent PROTOCOL.md ping/boot_status/framebuffer_capture table | OBSOLETE_ARCHITECTURE | Main is WP-011R.2 overlay protocol (`godot_input_overlay`, `browser_input_overlay`) |
| TOKENS_WP011.json from #103 | ALREADY_SUPERSEDED | Main has `RING_TO_REAL_APPLICATION_INPUT_PASS=true` (wave WP-011R.2); #103 has `false` and older timestamp |
| Connectivity / creator_studio / waike_app / privacy / launcher diffs | ALREADY_SUPERSEDED | Applying #103 would regress post-#116/#121 accepted-main |
| `artifacts/wp011r/**/*.log`, `*.png`, `*.ppm`, ring/browser collector artifacts | STALE_EVIDENCE_ONLY | Do not re-land as current evidence |
| `os_build/device_lab_interactive_guest/README.md` (210 lines, missing on main path) | STALE_EVIDENCE_ONLY | Documents a wave where Interactive Guest was “not yet built or booted”; current main already earned LIVE/DSXL/RING/FOUR_GAME tokens |

## Unique capabilities remaining to port

**None.** Do not cherry-pick #103 proof code onto current main. The click-collector and old protocol table would **lower** honesty relative to WP-011R.2.

## Owner action (not performed by Cursor)

1. Keep #103 open until you attach this note (or equivalent) on the PR.
2. Then close as superseded by accepted-main `d5c2d17` (Product-Use #116 + Stream A #117–#120 + supervisor-ready #121).
3. Do not merge. Do not use #103 screenshots/logs as current evidence.

Compared: 2026-08-19T03:25Z. Cursor never merges.
