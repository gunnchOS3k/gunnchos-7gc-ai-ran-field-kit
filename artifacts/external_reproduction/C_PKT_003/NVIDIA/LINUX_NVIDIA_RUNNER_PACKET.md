# Linux NVIDIA Runner Packet — C-PKT-003

## Purpose
Execute NVIDIA / Sionna / Aerial depth **only** on a Linux host with real CUDA + licensed stacks.  
Discovery Mac path remains **FAIL CLOSED** via `nvidia-6g-probe`.

## Preconditions
- Linux x86_64 (or supported NVIDIA ARM) with `nvidia-smi` working
- CUDA toolkit matching driver
- Optional: NGC access + Aerial SDK / pyAerial / AODT licenses as required by vendor docs
- Do **not** run large model + large Sionna + QEMU simultaneously if freemem unsafe

## Commands (on Linux GPU host)

```bash
# 1) Fail-closed probe (expect exit 0 only when GPU stack detectable)
python -m research.external_reproduction.cli.researcher_cli nvidia-6g-probe

# 2) Re-emit environment truth
python -m research.external_reproduction.cli.researcher_cli env

# 3) CPU Oulu packs still valid without GPU
python -m research.external_reproduction.cli.researcher_cli run --target ALL
```

## Forbidden claims on Mac / no-Aerial hosts
- `NVIDIA_AERIAL_VALIDATED`
- `AODT_VALIDATED` / `PYAERIAL_VALIDATED`
- `OTA` / `6G_CERTIFIED` / `CARRIER_ACCEPTED`
- Silent stub substitution for missing imports

## GPU NR baseband adjacency
If sibling `gunnchos-gpu-nr-baseband-platform` is present, use its CPU reference path first; CUDA path only when probe is non-fail-closed. See `GPU_NR_RUNNER_PACKET.md`.
