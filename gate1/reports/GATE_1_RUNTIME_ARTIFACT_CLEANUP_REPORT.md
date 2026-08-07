# GATE 1 Runtime Artifact Cleanup Report

Generated: 2026-08-07T20:48:01Z

## Policy
- Timestamped runtime outputs under `gate1/evidence/{pending,runs,accepted,rejected}` must not be git-tracked.
- Preserve `.gitkeep` only.
- Do **not** relabel software/runtime outputs as physical evidence.

## Actions taken
1. Classified each tracked file; hashed into `gate1/post_merge/runtime_artifact_migration_manifest.yaml`.
2. `git rm --cached` for timestamped JSON under pending/ and runs/.
3. Updated `.gitignore` with required evidence ignore rules.
4. Added deterministic fixtures under `gate1/fixtures/valid/` and `gate1/fixtures/invalid/`.
5. Orchestrator supports `--output-dir` and `--no-write`.
6. CI/test check: `scripts/check_gate1_runtime_artifacts_untracked.py`.

## Classifications
- RUNTIME_SOFTWARE_COMPONENT_PROBE
- RUNTIME_SOFTWARE_GAME_PROBE
- RUNTIME_RUN_AGGREGATE
- RUNTIME_STATUS_SNAPSHOT
- KEEP_GITKEEP

## Status
- Hygiene: complete locally
- Physical claim status: unchanged (still pending)
