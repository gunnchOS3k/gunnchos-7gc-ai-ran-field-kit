# LOCAL_NO_REPO_DISCOVERY_AUDIT

Generated during No-Repo local Pixel calibration continuation.

## Search roots

- `/Users/gunnchos/Downloads`
- `/Users/gunnchos/Documents` (empty / no matches)
- `/Users/gunnchos/Desktop` (empty / no matches)
- `/Users/gunnchos/Developer` (absent)
- `/Users/gunnchos/Projects` (absent)
- `/Users/gunnchos/repos` (absent)
- `$HOME` top-level scan via Downloads subtree

## Selected canonical copies

All selected under research product-spine:

| Repository | Absolute path | Remote | Selection reason |
|---|---|---|---|
| edge-io-measurement-node | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/edge-io-measurement-node` | `gunnchOS3k/edge-io-measurement-node` | Correct remote; product-spine; clean tree; continuation branch fetched to PR #22 head |
| 7gc-digital-twin | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/7gc-digital-twin` | `gunnchOS3k/7gc-digital-twin` | Correct remote; product-spine; clean; on `main` after Gate 3 promotion merge |
| spectrumx-ai-ran-gary | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/spectrumx-ai-ran-gary` | `gunnchOS3k/spectrumx-ai-ran-gary` | Correct remote; product-spine; clean; preferred over dirty Downloads duplicate |
| ntn-resilience-sim | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/ntn-resilience-sim` | `gunnchOS3k/ntn-resilience-sim` | Correct remote; product-spine; continuation branch = PR #24 head |
| gunnchos-7gc-ai-ran-field-kit | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit` | `gunnchOS3k/gunnchos-7gc-ai-ran-field-kit` | Correct remote; product-spine; continuation branch = PR #5 head |
| readygary-6g-beam-selection | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/readygary-6g-beam-selection` | `gunnchOS3k/readygary-6g-beam-selection` | Correct remote; product-spine; preferred over alternate Downloads copy |

## Duplicate candidates (rejected)

| Candidate | Remote | Branch / HEAD | Dirty | Decision | Reason |
|---|---|---|---|---|---|
| `/Users/gunnchos/Downloads/readygary-6g-beam-selection` | gunnchOS3k/readygary-6g-beam-selection | main / 82de516 | clean | rejected | Not under product-spine; older/alternate copy |
| `/Users/gunnchos/Downloads/spectrumx-ai-ran-gary` | gunnchOS3k/spectrumx-ai-ran-gary | feat/digital-twin-streamlit-fixes | dirty (~183) | rejected | Dirty unrelated worktree; left untouched |
| `.../gunnchos-lssmb-research-grade-completion/evidence/*` | n/a | n/a | n/a | rejected | Evidence snapshots, not git worktrees |
| `.../gunnchos-blockers-to-evidence-todos/issue_bodies/*` | n/a | n/a | n/a | rejected | Issue body folders, not repositories |

## Manifest

Machine-readable mapping: `/tmp/gunnchos_gate34_repo_manifest.json`

## Clones performed

None. All six required repositories already existed locally under the product-spine `repos/` directory.

## Notes

- Cursor workspace was intentionally No Repo; discovery used filesystem + git remotes only.
- Absolute paths used for all subsequent commands; no `.code-workspace` required.
