# Master Reference Remediation Report

Generated: 2026-08-06T20:16:55Z

## Policy
- canonical_default_branch: main
- legacy_default_branch: master
- new_master_references_prohibited: true
- master_deletion_requires_edmund_approval: true

## Allowlisted contexts
- Migration history and archival reports under program/reports/
- branch_migration_*.yaml
- Explicit dual-trigger workflow allowlist when documented

## Active config rule
`scripts/validate_main_branch_policy.py` fails if active configuration reintroduces `master` as default/base outside the allowlist.

## Notes
- Do not delete master in this pass.
- Historical prose mentioning master is permitted.
