# Portfolio GitHub App credential handoff

Status until secrets exist and App is installed:

```text
BLOCKED_CREDENTIAL_CONFIGURATION
```

## Required repository secrets (field-kit)

| Secret | Purpose |
|---|---|
| `PORTFOLIO_APP_ID` | GitHub App ID |
| `PORTFOLIO_APP_PRIVATE_KEY` | App private key PEM |

Optional fallback (not preferred):

| Secret | Purpose |
|---|---|
| `PORTFOLIO_REPO_READ_TOKEN` | Fine-grained PAT with Contents:Read on private siblings |

## App permissions

- Repository access: all locked private siblings (at minimum Oulu + NVIDIA baseband; preferably entire portfolio)
- Permissions: **Contents: Read-only**

## Workflow behavior

1. Mint token via `actions/create-github-app-token@v2`
2. Pass token only as `PORTFOLIO_CHECKOUT_TOKEN` env to `scripts/checkout_locked_repositories.py`
3. Reports set `token_exposed: false` and never include the token
4. Missing credentials → fail closed with `BLOCKED_CREDENTIAL_CONFIGURATION`

Do not commit keys. Do not print secrets.
