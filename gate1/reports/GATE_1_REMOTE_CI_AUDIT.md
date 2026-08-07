# GATE 1 Remote CI Audit

Generated: 2026-08-07T21:02:30Z

## Token
- `GATE_1_REMOTE_CI_PASS` (required Gate 1 workflows green on post-merge heads; see `GATE_1_REMOTE_CI_EVIDENCE.md`)

## Required workflow
- `.github/workflows/gate1-field-kit.yml` — Gate 0 + Gate 1 schemas/orchestrator, report freshness, physical-claim rejection, repo-lock, generated-artifact prohibition, main-branch policy
- Sibling `gate1-ci.yml` / Gate 1 post-merge integrity workflows on all eight component repos

## Existing workflows inventoried
- See `gate1/post_merge/ci_inventory.yaml`

## Triggers (gate1-field-kit)
- `pull_request`
- `push` to `main`
- `workflow_dispatch`

## Defaults
- `permissions: contents: read`
- Job timeouts + concurrency group cancel-in-progress

## Interpretation
- Local automation pass ≠ remote CI green (now recorded as PASS for required Gate 1 workflows).
- Do not advance to `GATE_1_PASS` from CI alone — physical evidence + Edmund acceptance still required.
- Prior interim token `GATE_1_REMOTE_CI_PENDING` is superseded by evidence in `GATE_1_REMOTE_CI_EVIDENCE.md`.
