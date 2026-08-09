# Continuation IX — Accepted Main Lock

Updated: 2026-08-09T20:31:13Z

Doctrine: `FULL_PRODUCT_ENTIRETY` + digital release lock attempt; `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.

Policy: accepted tips are **merged `origin/main` SHAs only** — never draft tips.

`digital_release_lock_complete=false` until DIGITAL blockers=0 on accepted mains after Cont IX sibling merges.

| Repo | origin/main SHA | Notes |
|------|-----------------|-------|
| gunnchos-7gc-ai-ran-field-kit | `7c6b955be933e050f81358f25077866f37a493bd` | Cont VIII #41 release-readiness closure on main; Cont IX lock base |
| gunnchos-hardware-industrial-design | `a710f35559252f36f0e6af7e025a5958df0906e3` | #51 Cont VIII manufacturer packages on main; DIGITAL residual (proxy/Radxa/silk) |
| edge-io-measurement-node | `a1cd2e95c62eb0eefd507b976158232b83f5b33b` | #35 Cont VIII ring E2E digital on main; physical boot still pending |
| gunnchos-device-os | `06366da047a6938646acb01e016d19318fabab70` | #67 Cont VIII release-readiness OS on main; Gate 1 may be red at kickoff; Cont IX OS PR must prove clean env (manifest-only productivity until then) |
| gunnchAI3k | `91a9f135b6423a7627ed61946b16e9ab9d79de6e` | #26 Cont VIII platform complete on main |
| anime-aggressors | `249270383eab87cf4d1240ea17e66bfff44d4b8c` | #70 Path A audit + RC hardening on main |
| pedestrian-pursuit | `a2c6da5b4d4635af1281dbb12b8564ba70f994c6` | #12 digital RC art/audio on main; physical FPS separate |
| archive-of-life-artifact-world | `948ca172bb77b4caf1bd3c2d809d74ee6d4b6c75` | #25 Cont VIII release integrity on main |
| beatlink-party | `e0c18f3dbb964608271c14611e1068cff9c17205` | #16 Cont VIII gunnchOS packaging on main |

Machine-readable: [`ACCEPTED_MAIN_LOCK.json`](../continuation_ix/ACCEPTED_MAIN_LOCK.json)
