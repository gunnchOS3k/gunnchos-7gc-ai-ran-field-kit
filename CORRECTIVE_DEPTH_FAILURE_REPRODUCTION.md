# Corrective-Depth Failure Reproduction

## Failure 1 — Gate 2 repository-lock verification mismatch

### Exact command

```bash
cd gunnchos-7gc-ai-ran-field-kit
python3 scripts/verify_repo_lock.py --repos-root ..
```

### Exact failed test

`tests/provenance/test_repo_lock_verify.py::test_repo_lock_matches_current_checkouts`

Also: Application Readiness check `verify_repo_lock`; Integrated pipeline `NON-REPRODUCIBLE` on edge-io commit.

### Expected

`{"ok": true}` when local required siblings match lock commits (and dirty prohibition policy).

### Actual

```json
{
  "ok": false,
  "failures": [
    "edge-io-measurement-node",
    "7gc-digital-twin",
    "spectrumx-ai-ran-gary",
    "ntn-resilience-sim"
  ]
}
```

Example delta: edge-io expected `3b42a7c…`, actual `b13156e…`.

### Root cause

`integration/repo-lock.json` stale (`locked_at: 2026-07-24`). Sibling Gate-6 harness commits advanced. Verify correctly refuses silent rewrite. No `make write-repo-lock` writer existed to regenerate explicitly.

### Affected files

- `integration/repo-lock.json`
- `scripts/verify_repo_lock.py`
- (missing) `scripts/write_repo_lock.py`
- `Makefile` target `write-repo-lock`
- `tests/provenance/test_repo_lock_verify.py`

### Corrective change

1. Add `scripts/write_repo_lock.py` + `make write-repo-lock` that writes enriched schema and **never** runs from `verify`.
2. Strengthen verify: schema validation, empty-commit reject, required-branch check, dirty prohibition, negative suite.
3. Regenerate lock via writer after corrective sibling SHAs are known (not during verify).

### Regression test

Negative: stale field-kit / Oulu / NVIDIA commits fail; missing required repo fails; dirty required fails; wrong branch fails; malformed lock fails; empty commit fails.  
Positive: exact clean checkouts at recorded commits pass.

---

## Failure 2 — Application readiness / valid rehearsal golden

### Exact command

```bash
python3 -m pytest -q tests/pilotctl/test_assignment_canonical_goldens.py::test_valid_rehearsal_golden
```

### Exact failed test

`tests/pilotctl/test_assignment_canonical_goldens.py::test_valid_rehearsal_golden`

### Expected

Valid golden fixture validates (`validate_assignment` ok) while preserving canonical hash bytes.

### Actual

Hash layer PASS (`digest == expected_hash`, canonical bytes match).  
`validate_assignment` → `ok: false`, errors: `["assignment expired"]` because fixture `expires_at: 2026-07-24T23:11:04Z` < wall clock on 2026-07-29.

### Root cause

Golden integrity coupled to wall-clock expiry. Canonicalization is **not** broken. Regenerating the golden solely to chase a clock would obscure the real API defect: fixture validation needs injectable reference time.

### Affected files

- `scripts/pilotctl.py` (`validate_assignment`)
- `tests/pilotctl/test_assignment_canonical_goldens.py`
- `fixtures/pilot_assignment/valid_rehearsal.json` (unchanged hash payload preferred)

### Corrective change

Add `validate_assignment(path, *, now: datetime | None = None)`. Golden test pins `now` inside `[created_at, expires_at)`. Live/CLI paths continue using wall clock. Keep `expired.json` failing under post-expiry `now`.

### Regression test

1. Valid golden with frozen in-window `now` passes.  
2. Key ordering / whitespace / semantic mutation / assignment / duration / session_type contracts unchanged.  
3. Expired fixture still fails when `now` ≥ `expires_at`.

---

## Failure 3 — Gate 6 sibling fallback success (integrity defect)

### Exact location

`scripts/run_gate6_dry_run.py` → `invoke_sibling_dry_runs()` wrote fallback note and returned `ok: True` on Make failure / missing rule.

### Corrective change

Fail closed. Require NVIDIA `make gate6-dry-run`. Parent `harness_ok` ∧= sibling success ∧ report schema validation.
