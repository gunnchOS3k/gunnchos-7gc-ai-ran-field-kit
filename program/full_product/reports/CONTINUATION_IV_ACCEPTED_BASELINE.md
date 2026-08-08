# Continuation IV — Accepted Baseline (immutable at start)

Updated: 2026-08-08T19:41:39Z

Doctrine: `FULL_PRODUCT_ENTIRETY_MODE=ACTIVE`; `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.
Policy: accepted tips are **merged `origin/main` SHAs only** — never `cursor/*` draft SHAs.

| Repo | origin/main SHA | Merged PRs | Notes |
|------|-----------------|------------|-------|
| field-kit | `7ebbe27bbae6980f0db8b5c14b39f2767b448128` | #33 | Umbrella artifact CI green after #33 |
| hardware | `79b11aba3ca9d4db7051b6d5ccb3571e72503396` | #46 | includes #46 family depth |
| edge-io | `fc617e831916362e77aa157d77d458e935dc4cfa` | #32 | RING_ZEPHYR_WEST_BUILD_PASS |
| device-os | `a4c17d298c6f4b769c96632646425c9168e3ef98` | #59,#58 | newer than Cont III listed 4ffe7f1; includes #59+#58 |
| gunnchAI3k | `223b2338364a637ae36c6d32a90393042ff4088c` | #22 | includes #22 local runtime/evals |
| anime | `0d965bc5709ebfd0c4e4e29d4a7dad0d68bf372a` | #67 | includes #67 Alpha-exit digital |
| pedestrian | `822d7eb4c75ba44b7fe88b2580fa7f933767d3a1` | #9 | includes #9 Godot headless |
| archive | `49b2bc4319399e0247884ed004fe54f8390cf04b` | #19 | includes #19 Alpha-exit digital |
| beatlink | `d2ef8d45bbe55790b21024b6307735c7c09979c8` | #10,#11 | newer than Cont III listed tip; #10+#11 |

## Carry-forward research siblings (not Cont IV product pins)

Research/twin repos remain tracked separately and are not Cont IV product acceptance tips.

Machine-readable: [`../_baseline_accepted_mains.json`](../_baseline_accepted_mains.json)
