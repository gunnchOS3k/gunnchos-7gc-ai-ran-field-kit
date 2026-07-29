#!/usr/bin/env python3
"""Edge-AI latency benchmark runner (records protocol fields; no fabricated device claims)."""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    k = (len(ys) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(ys) - 1)
    if f == c:
        return ys[f]
    return ys[f] + (ys[c] - ys[f]) * (k - f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="synthetic_matmul")
    parser.add_argument("--provider", default="numpy_cpu")
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "edge_ai" / "benchmark.json")
    args = parser.parse_args()

    import numpy as np

    n = 256
    a = np.random.randn(n, n).astype(np.float32)
    b = np.random.randn(n, n).astype(np.float32)
    for _ in range(args.warmup):
        _ = a @ b
    times = []
    for _ in range(args.samples):
        t0 = time.perf_counter_ns()
        _ = a @ b
        times.append(time.perf_counter_ns() - t0)

    commit = "unknown"
    try:
        import subprocess

        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        pass

    result = {
        "benchmark_id": "edge-ai-synthetic-matmul",
        "evidence_label": "CPU_MEASURED",
        "device": platform.node(),
        "runtime": platform.platform(),
        "provider": args.provider,
        "model": args.model,
        "input": {"shape": [n, n], "dtype": "float32"},
        "warm-up": args.warmup,
        "percentiles_ns": {
            "median": statistics.median(times),
            "p90": percentile(times, 90),
            "p95": percentile(times, 95),
            "p99": percentile(times, 99),
            "max": max(times),
        },
        "memory": None,
        "power_thermal": None,
        "commit": commit,
        "command": f"python3 scripts/run_edge_ai_benchmark.py --samples {args.samples}",
        "status": "OK",
        "note": "Synthetic CPU microbenchmark — not an NPU/GPU device claim",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
