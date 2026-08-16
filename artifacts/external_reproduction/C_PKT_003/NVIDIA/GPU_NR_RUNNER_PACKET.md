# GPU NR Runner Packet — C-PKT-003

## Sibling repo
`../gunnchos-gpu-nr-baseband-platform` (discovered by `research.external_reproduction.bridge.twin_bridge`)

## Policy
- Prefer CPU reference adapters when Aerial/CUDA unavailable
- Never invent Aerial PASS from Mac discovery host
- Soft AODT twin (`AODT_SOFT_TWIN.json`) is discovery-only

## Suggested Linux sequence
1. `python -m research.external_reproduction.cli.researcher_cli nvidia-6g-probe`
2. If status is `GPU_STACK_DETECTABLE`, follow gpu-nr-baseband README CUDA path
3. Record evidence under `artifacts/external_reproduction/C_PKT_003/NVIDIA/`
4. Keep SoA / OTA / CERTIFIED / CARRIER false unless separately earned
