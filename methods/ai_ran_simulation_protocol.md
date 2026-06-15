# AI-RAN Simulation Protocol

Canonical eval doc:

**[spectrumx-ai-ran-gary/docs/EVAL_PROTOCOL.md](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/blob/main/docs/EVAL_PROTOCOL.md)**

## Reproduce

```bash
git clone https://github.com/gunnchOS3k/spectrumx-ai-ran-gary.git
cd spectrumx-ai-ran-gary
pip install -r requirements.txt
make test
make benchmark
make ablation
```

## Outputs

| File | Content |
|------|---------|
| `results/benchmark/metrics.csv` | Multi-seed utilization, fairness, energy, latency proxy |
| `figures/benchmark/benchmark_metrics.png` | Benchmark plot |
| `results/ablation/ablation_table.csv` | Four-policy comparison |
| `figures/ablation/ablation_fairness_energy.png` | Ablation figure |

## Seeds

Default benchmark seeds: `42, 43, 44, 45, 46`. Ablation default seed: `42`.

## Non-claims

Synthetic policies are **not** near-RT RIC xApps and do not prove operational AI-RAN gains.
