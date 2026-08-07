# GATE 1 Remote CI Evidence

Generated: 2026-08-07T21:02:30Z

## Status
- `GATE_1_REMOTE_CI_PASS` (required Gate 1 workflows green on post-merge heads)

## Required workflow matrix (branch `cursor/gate1-post-merge-integrity-and-physical-closure`)

| Repository | Workflow | Head SHA | Conclusion | Run URL |
|---|---|---|---|---|
| gunnchos-device-os | Gate 1 post-merge integrity | c43f31d2b76a | success | https://github.com/gunnchOS3k/gunnchos-device-os/actions/runs/31217866154 |
| gunnchos-hardware-industrial-design | Gate 1 post-merge integrity | ad6b22803756 | success | https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/actions/runs/31217867758 |
| edge-io-measurement-node | Gate 1 post-merge integrity | 220b97f1b8cf | success | https://github.com/gunnchOS3k/edge-io-measurement-node/actions/runs/31218141333 |
| gunnchAI3k | Gate 1 post-merge integrity | ddb847ddae7a | success | https://github.com/gunnchOS3k/gunnchAI3k/actions/runs/31217876743 |
| beatlink-party | Gate 1 post-merge integrity | f98f39ca22b8 | success | https://github.com/gunnchOS3k/beatlink-party/actions/runs/31218155172 |
| archive-of-life-artifact-world | Gate 1 post-merge integrity | a61a054953e5 | success | https://github.com/gunnchOS3k/archive-of-life-artifact-world/actions/runs/31217887420 |
| pedestrian-pursuit | Gate 1 post-merge integrity | c8d1f909675c | success | https://github.com/gunnchOS3k/pedestrian-pursuit/actions/runs/31217892323 |
| anime-aggressors | Gate 1 post-merge integrity | fce3fa3ac883 | success | https://github.com/gunnchOS3k/anime-aggressors/actions/runs/31217895049 |
| gunnchos-7gc-ai-ran-field-kit | Gate 1 Field Kit | 7ecc50700fc3 | success | https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/actions/runs/31218320950 |

## Notes
- Non-Gate-1 workflows (e.g. beatlink full `CI` lint/typecheck, field-kit Application readiness / Gate 2) may still fail; they are **not** Gate 1 required checks for this closure packet.
- Local automation ≠ physical acceptance. `GATE_1_PASS` remains prohibited without Edmund-accepted physical evidence.
- Draft PRs only; Edmund remains sole merge approver.
