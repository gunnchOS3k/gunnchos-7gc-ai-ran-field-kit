# HUMAN_SECRET_BOOTSTRAP_REQUIRED

**Status:** `BLOCKED_CREDENTIAL_CONFIGURATION` until secrets exist and (for App path) the App is installed on private siblings.  
**No secrets are generated or stored in this file.**

Portfolio checkout automation needs **one** of the following in the field-kit GitHub Actions secrets (or local env for operator dry-runs — still never commit keys).

---

## Preferred: GitHub App (shortest browser path)

Creates `PORTFOLIO_APP_ID` + `PORTFOLIO_APP_PRIVATE_KEY`.

1. Open [https://github.com/settings/apps](https://github.com/settings/apps) (org apps: `https://github.com/organizations/<ORG>/settings/apps`).
2. **New GitHub App** → name it (e.g. `gunnchos-portfolio-checkout`) → Homepage URL can be the field-kit repo URL.
3. Uncheck webhook **Active** (not required for mint-token checkout).
4. **Repository permissions** → **Contents: Read-only**. Leave other permissions No access.
5. **Where can this GitHub App be installed?** → Only on this account / selected accounts as appropriate.
6. **Create GitHub App** → copy **App ID** → this is `PORTFOLIO_APP_ID`.
7. **Generate a private key** → download the `.pem` → entire PEM is `PORTFOLIO_APP_PRIVATE_KEY` (including `BEGIN`/`END` lines).
8. **Install App** → choose the account → grant access to **all locked private sibling repos** needed by `CROSS_REPO_VERSION_LOCK` (at minimum Oulu + NVIDIA baseband; preferably entire portfolio).
9. In the **field-kit** repo: **Settings → Secrets and variables → Actions** → add:
   - `PORTFOLIO_APP_ID`
   - `PORTFOLIO_APP_PRIVATE_KEY`
10. Re-run the portfolio checkout workflow. Expect `actions/create-github-app-token@v2` → `PORTFOLIO_CHECKOUT_TOKEN` env only inside `scripts/checkout_locked_repositories.py` (`token_exposed: false`).

Do not paste the PEM into chat, issues, or git.

---

## Fallback: Fine-scoped PAT

Creates `PORTFOLIO_REPO_READ_TOKEN` (not preferred).

1. Open [https://github.com/settings/personal-access-tokens](https://github.com/settings/personal-access-tokens) → **Generate new token** (fine-grained).
2. Resource owner = account that owns the private siblings.
3. Repository access → **Only select repositories** → select the locked private siblings.
4. Permissions → **Repository → Contents: Read-only**. No admin, no workflows write, no secrets.
5. Generate → copy token once → store as Actions secret `PORTFOLIO_REPO_READ_TOKEN` on field-kit.
6. Prefer rotating / deleting after App path is live.

---

## Verification (no secret print)

```bash
# In CI: missing credentials must fail closed with BLOCKED_CREDENTIAL_CONFIGURATION
# Locally: only check that secret *names* are configured in the repo settings UI — do not echo values
```

See also: `gunnchos-7gc-ai-ran-field-kit/PORTFOLIO_APP_CREDENTIAL_HANDOFF.md`
