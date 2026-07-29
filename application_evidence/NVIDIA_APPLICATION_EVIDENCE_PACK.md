# NVIDIA Aerial Application Evidence Pack

{
  "pack": "nvidia_aerial",
  "generated_at": "2026-07-29T19:02:35Z",
  "architecture": "C++20 CPU reference + conditional CUDA NR baseband vertical slice, FAPI-like, fronthaul emulator, benchmark harness",
  "repository": "/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-gpu-nr-baseband-platform",
  "commit": null,
  "paper": "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
  "code_map": [
    "include/nr_bb/",
    "src/",
    "cuda/",
    "benchmarks/",
    "tests/"
  ],
  "phy_mac_coverage": [
    "PUSCH-oriented chain",
    "MIMO ZF/MMSE",
    "PF scheduler",
    "FAPI-like",
    "RU emulator"
  ],
  "traceability": "3GPP-oriented notes without conformance claims",
  "benchmark_method": "Percentile latency/throughput manifests per schemas/benchmark_result.schema.json",
  "lab_readiness": "Protocols + dry-runs present; physical GPU/NIC/SDR PENDING",
  "upstream_contribution": "DOCUMENTED_IMPLEMENTATION (not upstream-accepted)",
  "exact_external_gaps": [
    "eight-plus years of work-related industry experience \u2014 NOT SATISFIED by repositories",
    "real telecom customer/partner field trials \u2014 PENDING / BLOCKED_EXTERNAL",
    "regulated commercial product ownership \u2014 NOT CLAIMED"
  ],
  "statuses": [
    "GATE4_NVIDIA_PORTABLE_PASS (if CPU tests pass)",
    "GATE4_NVIDIA_GPU_PENDING on Apple M2 host",
    "NVIDIA_TENURE_REQUIREMENT_UNSATISFIED",
    "NO_ACCEPTANCE_GUARANTEE"
  ],
  "host": {
    "hostname": "Edmunds-MacBook-Pro.local",
    "os": "Darwin 25.5.0",
    "machine": "arm64",
    "processor": "arm",
    "python": "3.11.2",
    "cuda": {
      "nvidia_smi": false,
      "nvcc": false,
      "torch_cuda": false,
      "gpu_name": null,
      "status": "BLOCKED_HARDWARE"
    },
    "docker": false,
    "captured_at": "2026-07-29T19:02:35Z"
  }
}
