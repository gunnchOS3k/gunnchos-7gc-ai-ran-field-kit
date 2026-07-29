# Remote CI Failure Reproduction

## Failure 1 — Application Readiness: private sibling clone

### Workflow / Job / Step

- Workflow: Application readiness CI
- Run ID: `30489513914`
- Commit: `de818fbe371ee87557d9a171626985536ff5578d` (merge of PR #11 → master)
- Job: `readiness`
- Step: `Checkout locked sibling repositories`

### Command

```bash
bash scripts/ci_checkout_locked_siblings.sh "$(dirname "$GITHUB_WORKSPACE")"
```

Internal:

```bash
git clone --no-checkout https://github.com/gunnchOS3k/gunnchos-emergent-service-intent-protocols.git ...
git clone --no-checkout https://github.com/gunnchOS3k/gunnchos-gpu-nr-baseband-platform.git ...
```

### Expected

Required locked siblings clone at exact SHAs; script exits 0.

### Actual

```text
fatal: could not read Username for 'https://github.com': No such device or address
FAILURES [
  "gunnchos-emergent-service-intent-protocols: ... exit status 128",
  "gunnchos-gpu-nr-baseband-platform: ... exit status 128"
]
```

Public-or-accessible siblings (edge-io, twin, spectrumx, ntn, hardware, device-os, readygary) cloned successfully without extra secrets.

### Root cause

Oulu and NVIDIA repositories are **private**. Unauthenticated `git clone` cannot access them. `ci_checkout_locked_siblings.sh` does not use a GitHub App installation token or PAT. Default `GITHUB_TOKEN` is not injected into the bash clone URLs.

### Corrective change

1. Prefer `actions/create-github-app-token` with `PORTFOLIO_APP_ID` + `PORTFOLIO_APP_PRIVATE_KEY`.
2. Pass opaque token only via env into `scripts/checkout_locked_repositories.py`.
3. Clone via `https://x-access-token:$TOKEN@github.com/...` without echoing token or writing token into reports.
4. If App secrets missing → `BLOCKED_CREDENTIAL_CONFIGURATION` (fail closed, never fake success).

### Regression test

- Checkout report schema with `credential_source`, `token_exposed: false`.
- Missing-required-private-repo → non-zero without fabricating checkout_status success.

---

## Failure 2 — Gate 2: provenance lock tests

### Workflow / Job / Step

- Workflow: Gate 2 Integrated System
- Run ID: `30489512237`
- Job: `gate2`
- Step: `Schema and failure tests`

### Failed tests

1. `tests/provenance/test_repo_lock_verify.py::test_repo_lock_matches_current_checkouts`
2. `tests/provenance/test_repo_lock_verify.py::test_dirty_required_repository_fails_when_prohibition_on`

### Root cause

1. Lock now requires Oulu, NVIDIA, hardware, device-os. Gate2 workflow only checks out the historical five siblings → required components missing → `verify(..., allow_dirty=True)` fails.
2. Dirty-tree test depended on incidental checkout dirtiness / missing siblings. When `dirty_required` empty but required siblings missing, `else: assert result["ok"]` fails.

### Corrective change

1. Checkout **all** locked required siblings in Gate2 using App token (same helper).
2. Rewrite dirty-tree test against an **isolated temporary Git repository**.
3. Match test runs against checked-out locked SHAs only after checkout step; keep negative drift tests on tmp locks.

### Regression test

- Isolated dirty-tree positive/negative in tmp repos.
- Match test green on Ubuntu with locked siblings checked out.
