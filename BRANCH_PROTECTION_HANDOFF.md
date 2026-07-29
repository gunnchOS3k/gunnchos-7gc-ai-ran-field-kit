# Branch Protection Handoff

Status: `BLOCKED_REPOSITORY_ADMIN_PERMISSION` until Edmund applies settings.

## Targets

- `gunnchos-7gc-ai-ran-field-kit` → `master`
- `gunnchos-emergent-service-intent-protocols` → `main`
- `gunnchos-gpu-nr-baseband-platform` → `main`

## Required settings

- Pull request required before merge
- Required status checks (field-kit):
  - Gate 2 Integrated System
  - Application readiness CI
  - Gate 3 Evidence Readiness
  - Gate 4 Evaluation Readiness
  - Umbrella Artifact CI
- Do not allow merge while checks pending/failing
- Restrict direct pushes to default branch
- Disable force pushes
- Disable branch deletion
- Conversation resolution required where supported
- Edmund remains final approver (no auto-merge)

## `gh api` example (field-kit master)

```bash
gh api -X PUT repos/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/branches/master/protection \
  -H "Accept: application/vnd.github+json" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Gate 2 Integrated System",
      "Application readiness CI",
      "Gate 3 Evidence Readiness",
      "Gate 4 Evaluation Readiness",
      "Umbrella Artifact CI"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

Repeat for Oulu/NVIDIA `main` with their native CI job names.

## Credential prerequisite for green Application Readiness / Gate 2

Install a GitHub App with **Contents: Read** on all portfolio private siblings, then set repository secrets on field-kit:

- `PORTFOLIO_APP_ID`
- `PORTFOLIO_APP_PRIVATE_KEY`

Do not commit keys. Do not echo secrets in logs.
