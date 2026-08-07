#!/usr/bin/env python3
"""Field connectivity collector — software harness (no real field claim)."""
from __future__ import annotations
import argparse, json, time, random
from pathlib import Path
from datetime import datetime, timezone
BEARERS = ["wifi", "ethernet", "cellular", "ntn_capability_stub"]
def sample(bearer: str, emulate: bool) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    if not emulate:
        return {"ts": now, "bearer": bearer, "status": "HARDWARE_PENDING", "evidence_class": "HARDWARE_PENDING"}
    return {"ts": now, "bearer": bearer, "status": "EMULATED", "latency_ms": round(random.uniform(10,120),2),
            "jitter_ms": round(random.uniform(1,20),2), "loss_pct": round(random.uniform(0,2),3),
            "throughput_mbps": round(random.uniform(5,200),2), "evidence_class": "SIMULATED"}
def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--emulate", action="store_true"); ap.add_argument("--seconds", type=int, default=2)
    args = ap.parse_args(); rows=[]
    end=time.time()+args.seconds
    while time.time()<end:
        for b in BEARERS: rows.append(sample(b, args.emulate))
        time.sleep(0.2)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"collector":"gate4.connectivity","rows":rows}, indent=2))
    print(f"wrote {args.out} rows={len(rows)}"); return 0
if __name__ == "__main__": raise SystemExit(main())
