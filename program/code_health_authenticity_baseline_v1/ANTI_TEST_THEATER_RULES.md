# Anti-Test-Theater Rules

## Intent
Prevent proof machinery from simulating product success without exercising production.

## Hard bans (S0) — require capability-closure (all five criteria)
S0 is **not** assigned from a regex token alone. All of the following must hold:
active first-party reachability; requirement/capability linkage; authenticity
falsification path; not token-alone; semantic review confirmed.

Typical S0 shapes (when closure is proven):
1. Tautological `assert True` / `expect(true).toBe(true)` as the sole gate assertion
2. Empty `pass` test bodies that close a claimed capability
3. Explicit `ALWAYS_PASS` / `FORCE_PASS` / `SKIP_ASSERT` / `assert 1 == 1` gates (word-boundary)
4. Fixtures or synthetic data labeled as `PRODUCTION_OR_FIELD` / L6 production evidence

`expect(<expr>).toBe(true)` for a non-literal boolean oracle is **not** theater.

## High risk (S1) — active first-party + material capability weakness
1. Asserting a value equals itself with no production call
2. Mutation survival / E2E bypass / duplicate divergence with evidence
3. Snapshot-only “behavior” claims with no semantic oracle
4. Completion/verification tokens sourced only from test-tree artifacts
5. Skipped suites that still contribute to PASS ledgers (skip/todo **alone** is not S1)

## Calibration exclusions
- `.venv/**`, `site-packages/**`, `node_modules/**`, `vendor/**` → excluded from S0/S1
- `legacy|deprecated|archive|old|prototype` → S0/S1 only if actively reachable; else ≤S2/S3
- `artifacts/**` → not automatically active
- S0/S1 totals are **root causes** after dedup (see `RAW_PATTERN_OBSERVATIONS.json`)

## Medium (S2)
1. Broad `except Exception: pass` / `return True` in proof paths
2. Hardcoded `"status": "PASS"` without computed checks
3. Sleep-then-assert synchronization as the only concurrency proof
4. Copy-paste tautological string asserts

## Low (S3)
1. Debug prints left as primary test output
2. Skips without ticket/reason

## Enforcement
Static scan in `tools/code_integrity/`. Findings are recorded. **CI for this baseline does not fail solely because S0/S1 findings exist** — they must remain visible.
