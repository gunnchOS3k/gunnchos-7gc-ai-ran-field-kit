# R6G Digital Replication — Environment

## Required

- Python 3.11+ recommended (3.10+ acceptable)
- stdlib only for replication core (no GPU required)
- pytest for tests

## Install

```bash
python3 -m pip install -r requirements.txt
# tests
python3 -m pip install pytest
```

## OS

Developed/verified on macOS; Linux CI expected. No root, no specialized RF hardware.

## Non-goals this cycle

- CUDA / Sionna GPU stacks
- ns-3 full-system campaigns
- QEMU (may be owned by Product-Use stream)
- Physical SDR/OTA benches

## Hashing

Raw JSON files are written with sorted keys; SHA-256 digests are recorded in the suite for primary R6G-003 seed runs.
