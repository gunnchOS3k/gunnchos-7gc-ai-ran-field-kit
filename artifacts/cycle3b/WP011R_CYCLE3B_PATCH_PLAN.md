# WP-011R Cycle 3B — earn LIVE/DSXL/RING/FOUR_GAME (honest)

Tip baseline: device-os `d57fba4` on DRAFT #103.
Prefer FAIL over false PASS. Cursor never merges. WP-001 DO_NOT_START.

## Keep true
- ECO010_SOAK_PASS
- GUEST_DUAL_OUTPUT_PASS

## Engineering fixes required (code on device-os worktree)

### LIVE
- Cause: Super+s before-frame returned `bytes=0` (race/empty PNG); after nonblank; marker in mousepad OK.
- Fix:
  1. Hot-patch guest agent reliably (prior `guest_bash_timeout`).
  2. Clear screenshot dir before each capture; retry framebuffer_capture until `bytes>4096` and nonblank (≤5 tries).
  3. Wait for mousepad paint before first capture.
  4. Commit `shell_app_before.png` + `shell_app_after.png` with distinct sha256.
  5. Never accept RFB/host screendump alone.

### DSXL
- Cause: sysfs `echo off` left DRM `connected→connected` (noop); window `output_id` invented then self-demoted.
- Fix:
  1. Host QEMU monitor `qom-set` secondary virtio-gpu output `xres/yres=0` (real disconnect); restore non-zero for reconnect.
  2. Prove mid status `disconnected` via guest `/sys/class/drm/card0-Virtual-2/status`.
  3. Placement: position foot left / mousepad right; prove via left/right halves of guest FB (distinct nonblank hashes) — set `placement_proven=true` only with that evidence.
  4. Focus: click each half + observable app mutation per output.

### RING
- Cause: apt only installed `grim`; libreoffice/labwc missing (`binary_not_installed:libreoffice`); mousepad-alone rejected.
- Fix:
  1. Diagnose guest apt log; ensure usernet + disk headroom; retry libreoffice-writer install until `command -v libreoffice`.
  2. Full Ring stack → uinput → LibreOffice ODT/text mutation + browser + one game state mutation.
  3. Leave false if any of three missing.

### FOUR_GAME
- Cause: Godot4 linux.arm64 download SSL failed on host urllib; Chromium web ≠ Pedestrian PASS.
- Fix:
  1. Host `curl` (SecureTransport) → `artifacts/wp011r/cache/Godot_v4.3-stable_linux.arm64`.
  2. `file_put` into guest `/opt/gunnchos/bin/godot`; deploy sibling `pedestrian-pursuit`.
  3. Prove Wayland Godot alive + input + `pp_progression.cfg` (or equivalent user:// save).
  4. Aggregate PASS only if all four in-guest earns; Pedestrian must be GUEST_GODOT4.

## Process
1. Implement fixes on `operating-cycle-3a/wp-011r-lab-10-acceptance`.
2. Run `scripts/run_cycle3b_demoted_reearn.py`.
3. Update TOKENS + gaps honestly; push DRAFT #103.
4. Update field-kit #71 A–Z; Edmund do-not-merge until independent accepts.
