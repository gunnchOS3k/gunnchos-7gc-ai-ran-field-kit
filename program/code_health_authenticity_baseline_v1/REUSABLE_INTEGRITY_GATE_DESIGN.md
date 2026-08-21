# Reusable Integrity Gate Design

## Goal
A repeatable gate that measures production authenticity and maintainability across the canonical 17-repo set without mutating product behavior.

## Inputs
- `ACCEPTED_MAIN_MANIFEST.json` — live merged `origin/main` SHAs only
- Local spine checkouts (or git archives) at those SHAs
- Synthetic controls under `program/code_health_authenticity_baseline_v1/controls/`

## Pipeline
1. **Controls** — negative fixtures must detect theater/coupling; positive fixtures must stay clean (`FAIL_AUDIT_INTEGRITY` if not)
2. **Path classification** — PRODUCTION / PROOF / DOCS / CI / AMBIGUOUS / OTHER
3. **Proof independence** — temp worktree; strip proof dirs; rescan production imports
4. **Dependency boundaries** — import/require edges; ecosystem Mermaid + PlantUML
5. **Canonical vs wave duplicates** — path heuristics for wave mirrors / `_gha_authoritative`
6. **Anti-test-theater** — S0–S3 static patterns
7. **Runtime authenticity matrix** — entrypoints × tests × coupling
8. **Mutation sampling** — up to 3 meaningful mutations per repo in temp worktrees (never committed)
9. **Complexity / orphans / fixtures / docs maps**
10. **Remediation register R1–R8** — no Baseline count changes
11. **Result token** — `BASELINE_COMPLETE_WITH_FINDINGS` | `BASELINE_COMPLETE_NO_CRITICAL_FINDINGS` | `BLOCKED_INCOMPLETE_AUDIT` | `FAIL_AUDIT_INTEGRITY`

## CI contract
- Workflow: `Code Health & Authenticity Baseline`
- Must verify controls + artifact presence + runner exit
- **Must not** fail merely because genuine S0/S1 findings were recorded
- Cursor never merges; draft PR only

## Prototype location
`tools/code_integrity/run_baseline_audit.py`

## Invocation
```bash
make code-health-authenticity-baseline
# or
python3 tools/code_integrity/run_baseline_audit.py
```
