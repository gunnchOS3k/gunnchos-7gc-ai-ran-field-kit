# Continuation VI — Accepted Baseline (immutable at start)

Updated: 2026-08-08T21:03:46Z

Doctrine: `FULL_PRODUCT_ENTIRETY_MODE=ACTIVE`; `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.
Policy: accepted tips are **merged `origin/main` SHAs only** — never `cursor/*` draft SHAs.

| Repo | origin/main SHA | Merged PRs | Notes |
|------|-----------------|------------|-------|
| field-kit | `2d257be6eb19b8237bf681b40f89275492fbd359` | #37 | Cont V lane draft registry #37 on main; Cont VI reproof base |
| hardware | `38b37221074446730709af5682a06cb4cefd39fc` | #48 | includes #48 hardware release / component truth |
| edge-io | `4507c8fc9efc07a9f2debeef89f5f60f5ae97e5c` | #33 | RING_ZEPHYR_WEST_BUILD_PASS + pinout parity stubs; firmware still smoke-only |
| device-os | `12ca8591202f59fdff962a4460323c6cfd67238d` | #62 | #62 on main CI RED (qemu TCG); open #63 bd68181 green MERGEABLE not merged — not accepted tip |
| gunnchAI3k | `ea630ec4dc09680dbbb5593c00f0e64d1cb23ec5` | #24 | includes #24 callable service; FULL platform not claimed |
| anime | `b3c823cf277c97c691a31ffc865798561e13a6eb` | #69 | #69 Path A cleared blocks_token; Beta/RC re-earn audited Cont VI |
| pedestrian | `ce0687d442311dee54bbfa9eedc7be9db8579650` | #11 | #11 competitive AI + Local MP; digital RC PARTIAL pending final art/audio |
| archive | `ee8a2e6346bbc384eda05217710fa4d1dd827e52` | #21 | #21 production ingest scoped Beta/RC; not global complete |
| beatlink | `c8a2de8c51929d776eea7b219f6015e787e0f174` | #13 | #13 Redis/load/mic; Beta/RC deliberately revoked pending Cont VI re-earn |

## Carry-forward research siblings (not Cont VI product pins)

Research/twin repos remain tracked separately and are not Cont VI product acceptance tips.

Machine-readable: [`../_baseline_accepted_mains.json`](../_baseline_accepted_mains.json)
