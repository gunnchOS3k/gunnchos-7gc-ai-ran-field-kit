# NVIDIA Aerial Application Evidence Pack

Visibility/publication: `BLOCKED_USER_APPROVAL` / `REVIEWER_ACCESS_BLOCKED_USER_APPROVAL`

{
  "pack": "nvidia_aerial",
  "generated_at": "2026-07-29T20:35:10Z",
  "owner_name": "gunnchOS3k/gunnchos-gpu-nr-baseband-platform",
  "repository_url": "https://github.com/gunnchOS3k/gunnchos-gpu-nr-baseband-platform",
  "canonical_repository_url": "https://github.com/gunnchOS3k/gunnchos-gpu-nr-baseband-platform",
  "branch": "cursor/corrective-depth-gates-4-6",
  "commit": "48164c8af83e6e3a27a1d21cb19025e9bcc15ba6",
  "release_candidate_tag": null,
  "visibility": "private",
  "reviewer_access": "REVIEWER_ACCESS_BLOCKED_USER_APPROVAL",
  "publication_status": "BLOCKED_USER_APPROVAL",
  "architecture": "C++20 CPU reference + conditional CUDA NR baseband path; educational modules separated; FAPI-like / fronthaul emulator; benchmark harness",
  "paper": "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
  "manuscript_artifact": "paper/CPU_GPU_NIC_NR_BASEBAND_BENCHMARK.md",
  "reproduction_command": "make bootstrap && make test && make gate4-cpu-reference && make gate6-dry-run && make paper",
  "code_map": [
    "include/nr_bb/",
    "src/",
    "educational/",
    "cuda/",
    "benchmarks/",
    "tests/"
  ],
  "phy_mac_coverage": [
    "PUSCH-oriented chain",
    "MIMO ZF/MMSE",
    "scheduler path",
    "FAPI-like",
    "RU emulator"
  ],
  "traceability": "3GPP-oriented notes without conformance claims",
  "benchmark_method": "Percentile latency/throughput manifests; GPU numeric results forbidden without NVIDIA hardware",
  "lab_readiness": "Protocols + dry-runs present; physical GPU/NIC/SDR PENDING",
  "upstream_contribution": "DOCUMENTED_IMPLEMENTATION (not upstream-accepted)",
  "evidence_class": "CPU_MEASURED / BLOCKED_HARDWARE (GPU)",
  "evidence_status": "GATE4_NVIDIA_EDUCATIONAL_CPU_PASS",
  "aerial_status": "GATE4_NVIDIA_AERIAL_DEPTH_PENDING",
  "exact_external_gaps": [
    "eight-plus years of work-related industry experience \u2014 NOT SATISFIED by repositories",
    "real telecom customer/partner field trials \u2014 PENDING / BLOCKED_EXTERNAL",
    "regulated commercial product ownership \u2014 NOT CLAIMED"
  ],
  "statuses": [
    "GATE4_NVIDIA_EDUCATIONAL_CPU_PASS",
    "GATE4_NVIDIA_AERIAL_DEPTH_PENDING",
    "GATE4_NVIDIA_GPU_PENDING",
    "NVIDIA_TENURE_REQUIREMENT_UNSATISFIED",
    "NVIDIA_CUSTOMER_TRIAL_REQUIREMENT_PENDING",
    "NO_ACCEPTANCE_GUARANTEE"
  ],
  "physical_blockers": [
    "NVIDIA GPU measurements",
    "Nsight",
    "NIC/PTP",
    "SDR/RU"
  ],
  "external_blockers": [
    "tenure gap",
    "customer trial",
    "upstream acceptance"
  ],
  "host_class": "author_laptop_cpu_only",
  "non_claims": [
    "NO_ACCEPTANCE_GUARANTEE",
    "no NVIDIA Aerial equivalence",
    "no 3GPP certification",
    "no carrier-grade claim"
  ]
}
