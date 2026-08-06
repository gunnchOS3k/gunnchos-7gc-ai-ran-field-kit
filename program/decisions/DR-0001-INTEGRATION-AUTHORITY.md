# DR-0001 — Integration Authority

## Decision
`gunnchos-7gc-ai-ran-field-kit` is the Gate 0–8 ecosystem control-plane and integration authority for requirements, claims, gates, evidence registries, and cross-repo version locks.

## Status
ACCEPTED for Gate 0 automated scaffolding.

## Consequences
- Other repositories remain owners of subsystem implementation.
- Field-kit does not claim those subsystems are complete merely by owning traceability.
- Existing artifacts (`CROSS_REPO_VERSION_LOCK.json`, `EXTERNAL_GATE_REGISTRY.json`, etc.) are preserved.
