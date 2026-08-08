# Continuation V — Accepted Baseline (immutable at start)

Updated: 2026-08-08T20:16:48Z

Doctrine: `FULL_PRODUCT_ENTIRETY_MODE=ACTIVE`; `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.
Policy: accepted tips are **merged `origin/main` SHAs only** — never `cursor/*` draft SHAs.

| Repo | origin/main SHA | Merged PRs | Notes |
|------|-----------------|------------|-------|
| field-kit | `0f998ef4567ffe5f54640f71df6951f90224a9e8` | #34,#35 | Umbrella Cont IV #34+#35 on main |
| hardware | `7e1658e63052e7baa2e9f4ab58113a91e4165c72` | #47 | includes #47 design-release candidates |
| edge-io | `fc617e831916362e77aa157d77d458e935dc4cfa` | #32 | RING_ZEPHYR_WEST_BUILD_PASS |
| device-os | `dee336a344bbc3ac730ed2cfd25a5f1d1e1af49f` | #61,#60 | includes #61+#60 bootable image + cloud/fleet DEV |
| gunnchAI3k | `6f98ab8b08851ad4e0ac8785bb409c248519b2b7` | #23 | includes #23 real local llama.cpp inference |
| anime | `1555ba3988b7026e418a0199cf5d10e1cfc384a8` | #68 | includes #68 Beta/RC digital (claim integrity audited) |
| pedestrian | `c8db661d6bf057c6c487586f378362005413bc1f` | #10 | includes #10 Beta digital / RC partial |
| archive | `5cb81fbd8de592a38e7e642185ef5e41e81aad98` | #20 | includes #20 Beta digital / Digital RC |
| beatlink | `dd9f32dbc550e28138d7764813ad07256bfffd6b` | #12 | includes #12 Beta Event Platform + Digital RC |

## Carry-forward research siblings (not Cont V product pins)

Research/twin repos remain tracked separately and are not Cont V product acceptance tips.

Machine-readable: [`../_baseline_accepted_mains.json`](../_baseline_accepted_mains.json)
