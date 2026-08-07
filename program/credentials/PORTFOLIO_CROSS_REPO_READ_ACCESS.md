# Portfolio Cross-Repo Read Access

Updated: `2026-08-07T22:19:36Z`

```text
PORTFOLIO_CROSS_REPO_READ_ACCESS_PASS
```

## Evidence (URLs only; no secrets)

- Application readiness CI (PR #18): https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/actions/runs/31223269294
- Gate 2 Integrated System (PR #18): https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/actions/runs/31223269436
- Checkout step: succeeded (Resolve checkout credential + Checkout locked sibling repositories green)
- Mechanism: per-repo read-only SSH deploy keys → field-kit Actions secrets `PORTFOLIO_SSH_KEY_*`
- App mint annotation may warn when App secrets absent; deploy keys are preferred path and were sufficient

## Private repos covered

- gunnchos-emergent-service-intent-protocols (deploy key read-only)
- gunnchos-gpu-nr-baseband-platform (deploy key read-only)

Public siblings use HTTPS/`GITHUB_TOKEN`.
