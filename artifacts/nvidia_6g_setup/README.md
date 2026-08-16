# NVIDIA 6G Phase 0 setup artifacts (non-secret)

Evidence from Mac bootstrap. Upstream clones live under `~/nvidia-6g-research/upstream` (not vendored here).

- No NGC keys, no API key material, no `.env` secrets.
- `AODT_EXECUTION_PASS` / pyAerial / Aerial GPU claims remain false until a real GPU worker run.
- Keychain service names only: `gunnchos-ngc-aodt`, `gunnchos-ngc-aerial`.
- `make nvidia-6g-probe` is expected to exit non-zero on Mac (FAIL_CLOSED).
