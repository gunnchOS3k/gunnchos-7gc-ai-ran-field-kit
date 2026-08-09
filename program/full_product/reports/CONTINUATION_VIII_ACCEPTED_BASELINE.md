# Continuation VIII — Accepted Main Baseline

Updated: 2026-08-09T19:13:58Z

Doctrine: `FULL_PRODUCT_ENTIRETY` + `DIGITAL_EXHAUSTION` + `PRE_MANUFACTURING_RELEASE`; `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.

Policy: accepted tips are **merged `origin/main` SHAs only** — never `cursor/*` draft SHAs.

| Repo | origin/main SHA | Last PR | Main CI | Notes |
|------|-----------------|---------|---------|-------|
| field-kit | `a4846ca970943ffc790298bc8bf36bf5c544c8b4` | #40 | green | Cont VII control-plane #40 on main; Cont VIII reproof base |
| hardware | `c5b6afd6a792d367593867fc7533f413a5146db4` | #50 | green | #50 Cont VIII EDA release-clean on main; structural HW only |
| edge-io | `a1cd2e95c62eb0eefd507b976158232b83f5b33b` | #35 | green | #35 Cont VIII ring E2E digital on main; physical boot still pending |
| device-os | `78cd33f1fde0a0c42eb6469bbdbe4664225d3dd0` | #66 | green | #65 schema quality/reliab + #66 real app packages on main |
| gunnchAI3k | `91a9f135b6423a7627ed61946b16e9ab9d79de6e` | #26 | green | #26 Cont VIII platform complete on main |
| anime | `249270383eab87cf4d1240ea17e66bfff44d4b8c` | #70 | green | #70 Path A audit + RC hardening on main |
| pedestrian | `a2c6da5b4d4635af1281dbb12b8564ba70f994c6` | #12 | green | #12 digital RC art/audio on main; physical FPS separate |
| archive | `948ca172bb77b4caf1bd3c2d809d74ee6d4b6c75` | #25 | green | #25 Cont VIII release integrity on main |
| beatlink | `e0c18f3dbb964608271c14611e1068cff9c17205` | #16 | green | #16 Cont VIII gunnchOS packaging on main |

Machine-readable: [`ACCEPTED_MAIN_BASELINE.json`](../continuation_viii/ACCEPTED_MAIN_BASELINE.json)

Cont VII SCHEMA_ONLY=4 is the prior freeze; Cont VIII re-proves after device-os #65+#66.
