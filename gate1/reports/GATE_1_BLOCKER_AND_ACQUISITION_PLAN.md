# GATE 1 Blocker and Acquisition Plan

Generated: 2026-08-07T20:48:01Z

## Current blockers

| Blocker | Class | Workstreams | Acquisition / recovery |
|---|---|---|---|
| Ring prototype not confirmed | REQUIRES_PHYSICAL_PROTOTYPE | ring-auth | Acquire/locate ring; re-run `operator.cli inventory`; operator confirm PRESENT_CONFIRMED |
| Dock station not confirmed | REQUIRES_PHYSICAL_PROTOTYPE | dock | Acquire/locate dock; inventory; confirm |
| Boot / AI / game target not confirmed | REQUIRES_LOCAL_HARDWARE | boot, ai-runtime, games | Provide representative device; install adb if Android; confirm |
| adb toolchain missing | REQUIRES_TOOLCHAIN | android targets | Install Android platform-tools; re-run inventory |
| Remote CI green missing | REMOTE_CI | all | Merge/run `gate1-field-kit` on main; attach evidence |

## Rules
- Do not invent hardware presence.
- Do not accept physical bundles without Edmund decision record.
- Do not start Gate 2 device vertical slices until `GATE_1_PASS` (physical) or explicit Edmund waiver.
