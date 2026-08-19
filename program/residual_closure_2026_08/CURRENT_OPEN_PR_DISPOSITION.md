# CURRENT_OPEN_PR_DISPOSITION

Generated: `2026-08-19T03:15:52Z`
Source: `gh pr list --state open` after `git fetch origin --prune` on all 17 in-scope repos.
Policy: Recommend only. Cursor never merges or auto-closes. Preview PR SHAs are **not** accepted-main.

## Prompt vs live GitHub

These were listed as open drafts in the residual-closure prompt. They are **MERGED** and belong in `CURRENT_ACCEPTED_MAIN.json`, not here:

| PR | State |
|---|---|
| gunnchAI #43 | MERGED 2026-08-19T03:08:16Z → `d357846` |
| ReadyGary #26 | MERGED 2026-08-19T01:56:26Z → `0e2a791` |
| portal #8 | MERGED 2026-08-18T22:10:41Z → `7842ff2` |
| anime #79, beatlink #23, edge-io #38, pedestrian #20, archive #33 | MERGED (Pixel 6a evidence) |
| spectrumx #101 | MERGED 2026-08-18T22:11:14Z → `cef3900` |

## Currently open (in-scope)

Disposition enum: `ACTIVE_CURRENT | REBASE_AND_VERIFY | SUPERSEDED_CLOSE | EVIDENCE_ONLY | OWNER_REVIEW | DO_NOT_MERGE_HISTORICAL`

### Must not merge

| Repo | # | Draft | Mergeable | Disposition | Rationale |
|---|---:|---|---|---|---|
| gunnchos-device-os | [103](https://github.com/gunnchOS3k/gunnchos-device-os/pull/103) | true | CONFLICTING | **DO_NOT_MERGE_HISTORICAL** | WP-011R lab remediations. Head `071f9b28`. Divergent vs accepted-main `d5c2d17`. Compare unique commits; port if still valuable; write owner supersession note. Do **not** close automatically. Do **not** re-land stale screenshots. |

### Product / path ambiguity (owner only)

| Repo | # | Draft | Mergeable | Disposition | Rationale |
|---|---:|---|---|---|---|
| anime-aggressors | [52](https://github.com/gunnchOS3k/anime-aggressors/pull/52) | false | MERGEABLE | OWNER_REVIEW | Unity launch experience vs Godot accepted-main. Destructive ambiguity. |
| anime-aggressors | [51](https://github.com/gunnchOS3k/anime-aggressors/pull/51) | false | UNKNOWN | OWNER_REVIEW | Unity environment rescue. Same path conflict. |

### Historical docs / readiness / hardening (not current digital product WIP)

| Repo | # | Draft | Disposition | Rationale |
|---|---:|---|---|---|
| gunnchAI3k | [18](https://github.com/gunnchOS3k/gunnchAI3k/pull/18) | false | OWNER_REVIEW | Mentorship docs |
| gunnchAI3k | [5](https://github.com/gunnchOS3k/gunnchAI3k/pull/5) | true | SUPERSEDED_CLOSE | Historical role-proof. Close only with supersession note. |
| gunnchAI3k | [4](https://github.com/gunnchOS3k/gunnchAI3k/pull/4) | true | EVIDENCE_ONLY | Historical portfolio hardening |
| waike-research-ops | [41](https://github.com/gunnchOS3k/waike-research-ops/pull/41) | false | OWNER_REVIEW | PhD application docs vs post-#52 main. Rebase before any merge. |
| gunnchos-7gc-ai-ran-field-kit | [75](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/75) | true | EVIDENCE_ONLY | Independent #74 VP landing |
| gunnchos-7gc-ai-ran-field-kit | [71](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/71) | true | SUPERSEDED_CLOSE | Cycle 3B burndown; superseded by #80+#81+#87. CONFLICTING. |
| gunnchos-7gc-ai-ran-field-kit | [1](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/1) | true | EVIDENCE_ONLY | Historical hardening |
| edge-io-measurement-node | [18](https://github.com/gunnchOS3k/edge-io-measurement-node/pull/18) | false | OWNER_REVIEW | PhD readiness |
| edge-io-measurement-node | [17](https://github.com/gunnchOS3k/edge-io-measurement-node/pull/17) | true | EVIDENCE_ONLY | Historical |
| edge-io-measurement-node | [16](https://github.com/gunnchOS3k/edge-io-measurement-node/pull/16) | false | OWNER_REVIEW | Oulu WCE alignment docs |
| edge-io-measurement-node | [8](https://github.com/gunnchOS3k/edge-io-measurement-node/pull/8) | false | SUPERSEDED_CLOSE | WAIKE_INTEGRATION.md |
| 7gc-digital-twin | [29](https://github.com/gunnchOS3k/7gc-digital-twin/pull/29) | true | SUPERSEDED | WP-012 README contract vs supervisor-ready #30 main |
| 7gc-digital-twin | [23](https://github.com/gunnchOS3k/7gc-digital-twin/pull/23) | false | OWNER_REVIEW | PhD readiness |
| spectrumx-ai-ran-gary | [99](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/99) | true | SUPERSEDED | README contract vs #100/#101 |
| spectrumx-ai-ran-gary | [93](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/93) | false | OWNER_REVIEW | PhD readiness |
| spectrumx-ai-ran-gary | [92](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/92) | true | EVIDENCE_ONLY | Historical hardening |
| spectrumx-ai-ran-gary | [91](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/91) | false | OWNER_REVIEW | Oulu WCE alignment |
| spectrumx-ai-ran-gary | [83](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/83) | false | SUPERSEDED_CLOSE | WAIKE_INTEGRATION.md |
| ntn-resilience-sim | [26](https://github.com/gunnchOS3k/ntn-resilience-sim/pull/26) | true | SUPERSEDED | README contract vs #27 |
| ntn-resilience-sim | [20](https://github.com/gunnchOS3k/ntn-resilience-sim/pull/20) | false | OWNER_REVIEW | PhD readiness |
| ntn-resilience-sim | [10](https://github.com/gunnchOS3k/ntn-resilience-sim/pull/10) | false | SUPERSEDED_CLOSE | WAIKE_INTEGRATION.md |
| readygary-6g-beam-selection | [22](https://github.com/gunnchOS3k/readygary-6g-beam-selection/pull/22) | false | OWNER_REVIEW | PhD readiness |
| readygary-6g-beam-selection | [21](https://github.com/gunnchOS3k/readygary-6g-beam-selection/pull/21) | true | EVIDENCE_ONLY | Historical |
| readygary-6g-beam-selection | [20](https://github.com/gunnchOS3k/readygary-6g-beam-selection/pull/20) | false | OWNER_REVIEW | Oulu WCE alignment |
| readygary-6g-beam-selection | [12](https://github.com/gunnchOS3k/readygary-6g-beam-selection/pull/12) | false | SUPERSEDED_CLOSE | WAIKE_INTEGRATION.md |
| anime-aggressors | [71](https://github.com/gunnchOS3k/anime-aggressors/pull/71) | true | SUPERSEDED | README contract vs #78/#79 |
| pedestrian-pursuit | [13](https://github.com/gunnchOS3k/pedestrian-pursuit/pull/13) | true | SUPERSEDED | README contract vs #19/#20 |
| archive-of-life-artifact-world | [26](https://github.com/gunnchOS3k/archive-of-life-artifact-world/pull/26) | true | SUPERSEDED | README contract vs #32/#33 |
| beatlink-party | [17](https://github.com/gunnchOS3k/beatlink-party/pull/17) | true | SUPERSEDED | README contract vs #22/#23 |
| gunnchos-research-portal | [5](https://github.com/gunnchOS3k/gunnchos-research-portal/pull/5) | true | OWNER_REVIEW | Role-proof landing pages |
| gunnchos-research-portal | [4](https://github.com/gunnchOS3k/gunnchos-research-portal/pull/4) | true | EVIDENCE_ONLY | Historical hardening |
| gunnchos-research-portal | [3](https://github.com/gunnchOS3k/gunnchos-research-portal/pull/3) | false | SUPERSEDED | Supervisor landing vs merged #7/#8 |
| gunnchos-research-portal | [1](https://github.com/gunnchOS3k/gunnchos-research-portal/pull/1) | false | OWNER_REVIEW | WAIKE/gunnchAI portal content |

### Repos with zero open PRs

- gunnchos-hardware-industrial-design
- gunnchos-gpu-nr-baseband-platform
- gunnchos-emergent-service-intent-protocols

## Counts (open only)

| Disposition | Count |
|---|---:|
| DO_NOT_MERGE_HISTORICAL | 1 (#103) |
| OWNER_REVIEW | 16 |
| SUPERSEDED / SUPERSEDED_CLOSE | 14 |
| EVIDENCE_ONLY | 7 |
| **Open total** | **38** |

None of these open PRs should be merged by this residual-closure agent. New work (if any) is **new narrowly scoped draft PRs from current origin/main**, not resurrection of the August 15 branch list.
