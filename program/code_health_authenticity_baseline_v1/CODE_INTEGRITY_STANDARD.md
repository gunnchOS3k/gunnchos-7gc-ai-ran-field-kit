# Code Integrity Standard — gunnchOS3k

## Purpose
Define what “implemented and tested” must mean for ecosystem repositories: production code is canonical, understandable, independent of proof machinery, and genuinely exercised by tests.

## Non-goals
- Not a requirement-completion wave
- Not a license to delete tests or product code to improve metrics
- Not an aggregate vanity percentage score

## Rules

### C1 — Canonical production
Runtime behavior must live in production paths (`src/`, `lib/`, `app/`, `cmd/`, game runtime trees, etc.). Wave mirrors, evidence trees, and harness outputs are not product.

### C2 — Proof independence
Production modules must not import `tests`, `fixtures`, `evals`, or evidence helpers. Removing proof trees in a temporary worktree must not be required for production to type/import-resolve for its own modules.

### C3 — Authentic tests
Tests must exercise production paths. Forbidden patterns include `assert True`, empty `pass` tests, always-pass gates, and fixtures labeled as production/field evidence.

### C4 — Architecture truth
Docs and UML must describe the code that exists on accepted `main`, not aspirational or wave-branch shapes.

### C5 — Maintainable structure
Hotspots, orphans, and duplicate wave implementations are recorded as findings. Remediation is tracked in families R1–R8 without changing Baseline requirement counts.

### C6 — Audit honesty
Serious findings are expected and valuable. CI for this baseline must not fail merely because genuine S0/S1 findings exist. Audit integrity controls (synthetic positive/negative fixtures) must pass.

## Severity
- **S0** Critical authenticity failure (theater / coupling that falsifies completion)
- **S1** High authenticity or maintainability risk
- **S2** Medium structural debt
- **S3** Hygiene / readability

## Ratings (no fake %)
`STRONG` | `ADEQUATE` | `NEEDS_WORK` | `CRITICAL` | `BLOCKED` | `NOT_APPLICABLE`
