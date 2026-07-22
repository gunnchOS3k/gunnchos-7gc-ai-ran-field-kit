# LOCAL_NO_REPO_BRANCH_SYNC_REPORT

Fetch: git fetch origin --prune on each canonical copy.

| Repo | Remote | Local branch | HEAD | Default | origin/default | Target branch | Target SHA | Dirty |
|---|---|---|---|---|---|---|---|---|
| edge-io-measurement-node | https://github.com/gunnchOS3k/edge-io-measurement-node.git | cursor/gate3-calibration-gate4-evaluation-3ec5 | ab9f263dce5e2b030aaea5eee24c25c42e50095f | main | 2b4434952e6a533dff451349a10eb587045dd9f7 | cursor/gate3-calibration-gate4-evaluation-3ec5 | ab9f263dce5e2b030aaea5eee24c25c42e50095f | clean |
| gunnchos-7gc-ai-ran-field-kit | https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit.git | cursor/gate3-calibration-gate4-evaluation-3ec5 | 4ab30a6c8215a6a5f968d88647e8bb4faefe708b | master | 6a239e942aef31088589190eaa0e290b095f5578 | cursor/gate3-calibration-gate4-evaluation-3ec5 | 4ab30a6c8215a6a5f968d88647e8bb4faefe708b | dirty |
| ntn-resilience-sim | https://github.com/gunnchOS3k/ntn-resilience-sim.git | cursor/gate3-calibration-gate4-evaluation-3ec5 | aef2678571bbfcfffc4c2734e608bd69ffa67c49 | main | 9055b806fa001b6b8d0130353d87668f038dce6e | cursor/gate3-calibration-gate4-evaluation-3ec5 | aef2678571bbfcfffc4c2734e608bd69ffa67c49 | clean |
| 7gc-digital-twin | https://github.com/gunnchOS3k/7gc-digital-twin.git | main | b036905df4f867aabdcc939ac646464874a3ee1f | main | b036905df4f867aabdcc939ac646464874a3ee1f | main | n/a (on default) | clean |
| spectrumx-ai-ran-gary | https://github.com/gunnchOS3k/spectrumx-ai-ran-gary.git | main | f7af6c7f7541360e07402f6927794116a1684d32 | main | f7af6c7f7541360e07402f6927794116a1684d32 | main | n/a (on default) | clean |
| readygary-6g-beam-selection | https://github.com/gunnchOS3k/readygary-6g-beam-selection.git | main | 525405cb19d7987ad218272f5897d4917c10dd75 | main | 525405cb19d7987ad218272f5897d4917c10dd75 | main | n/a (on default) | clean |

## PR association

- edge-io PR #22 -> cursor/gate3-calibration-gate4-evaluation-3ec5 @ ab9f263 (matched)
- field-kit PR #5 -> cursor/gate3-calibration-gate4-evaluation-3ec5 @ 4ab30a6 (matched)
- ntn PR #24 -> cursor/gate3-calibration-gate4-evaluation-3ec5 @ aef2678 (matched)

## Actions

- Checked out / fast-forwarded continuation branches for edge-io, field-kit, and ntn.
- Supporting repos checked out to origin/main (Gate 3 promotion merged).
- No force-push; no default-branch rewrite; no replacement PRs.
- Duplicate dirty copy under Downloads/spectrumx-ai-ran-gary left untouched.
