# GATE 1 Remote CI Audit

Generated: 2026-08-07T20:48:01Z

## Token
- `GATE_1_REMOTE_CI_PENDING`

## Required workflow
- `.github/workflows/gate1-field-kit.yml` — Gate 0 + Gate 1 schemas/orchestrator, report freshness, physical-claim rejection, repo-lock, generated-artifact prohibition, main-branch policy

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
- Local automation pass ≠ remote CI green.
- Do not advance to `GATE_1_PASS` from CI alone.
