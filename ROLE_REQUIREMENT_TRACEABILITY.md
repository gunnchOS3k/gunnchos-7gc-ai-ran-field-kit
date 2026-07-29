# Role Requirement Traceability — Gates 4–6

**Sources retrieved:** 2026-07-29 (see `requirements/sources/README.md`)  
**Owner:** Edmund Gunn, Jr.

| Role requirement | Evidence artifact | Gate | Automatable? | Status target |
|---|---|---|---|---|
| Oulu emergent semantic communication | Discrete learned protocol + interpretability scripts | 4A | Yes | `GATE4_OULU_AUTOMATED_PASS` |
| Oulu learning-based protocol design | MARL env + IPPO/MAPPO/VDN + comm baseline | 4A | Yes | same |
| Oulu cooperative multi-agent | UE/BS/edge/(NTN) agents | 4A | Yes | same |
| Oulu multi-objective optimization | Weighted / preference / Lagrangian / Pareto | 4A | Yes | same |
| Oulu state abstraction | Raw / engineered / learned | 4A | Yes | same |
| Oulu generative AI | Intent schema + rule parser + optional LLM adapter | 4A | Yes (LLM optional) | same |
| Oulu multimodal sensing | Radio + geometry + edge adapters | 4A | Yes (soft) | same |
| Oulu B5G/6G use cases | Congestion, TN/NTN, critical, education | 4A/6 | Synthetic yes; physical no | harness + pending field |
| Oulu publication potential | Manuscript + artifact + RC | 5 | Yes | `GATE5_RELEASE_CANDIDATE_PASS` |
| NVIDIA C/C++ baseband | C++20 PUSCH-oriented vertical slice | 4B | Yes | `GATE4_NVIDIA_PORTABLE_PASS` |
| NVIDIA CUDA/GPU | CUDA sources + real profiles | 4B/6 | Code yes; measure needs GPU | `GATE4_NVIDIA_GPU_PENDING` on this host |
| NVIDIA CPU/GPU/NIC optimization | Benchmark harness + ≥6 opt studies | 4/5/6 | CPU yes; NIC/GPU blocked | partial |
| NVIDIA PHY/MAC knowledge | PUSCH, MIMO, scheduler, FAPI-like | 4B | Yes | portable pass |
| NVIDIA low-level 3GPP view | Spec traceability notes + vectors | 4/5 | Yes (no conformance claim) | documented |
| NVIDIA lab integration | SDR/instrument/e2e packet | 6 | Harness yes | `GATE6_HARNESS_PASS` |
| NVIDIA test tools | Bench/vector/fault/FAPI tools | 4B | Yes | portable pass |
| NVIDIA customer/partner field trials | Real external trial | external | **No** | `BLOCKED_EXTERNAL` |
| NVIDIA regulated-radio experience | Compliance + industry evidence | 6+ext | Partial harness | pending |
| NVIDIA technical leadership | Architecture + upstream draft | 4/5 | Yes (upstream merge external) | documented |
| NVIDIA 8+ years experience | Employment history only | external | **No** | `NVIDIA_TENURE_REQUIREMENT_UNSATISFIED` |

## Explicit non-claims

- No Oulu admission guarantee  
- No NVIDIA hiring guarantee  
- No 3GPP conformance certification  
- No carrier-grade product claim  
- No fabricated tenure or customer trials  
