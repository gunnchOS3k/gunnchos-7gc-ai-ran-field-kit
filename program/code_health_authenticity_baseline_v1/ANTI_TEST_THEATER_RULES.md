# Anti-Test-Theater Rules

## Intent
Prevent proof machinery from simulating product success without exercising production.

## Hard bans (S0)
1. `assert True` / equivalent tautologies as the sole assertion
2. Empty `pass` test bodies
3. `ALWAYS_PASS` / `FORCE_PASS` / `assert 1 == 1` gates
4. Fixtures or synthetic data labeled as `PRODUCTION_OR_FIELD` / L6 production evidence

## High risk (S1)
1. Asserting a value equals itself with no production call
2. Mocking the entire system under test, then asserting mock echoes
3. Snapshot-only “behavior” claims with no semantic oracle
4. Completion/verification tokens sourced only from test-tree artifacts
5. Skipped suites that still contribute to PASS ledgers

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
