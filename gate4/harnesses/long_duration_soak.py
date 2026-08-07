#!/usr/bin/env python3
"""Multi-hour soak harness with rotation + redaction hooks."""
from __future__ import annotations
import argparse, json, time, hashlib
from pathlib import Path
from datetime import datetime, timezone
REDACT={"ssid","imsi","phone","email","token"}
def redact(obj): return {k:("***" if k.lower() in REDACT else v) for k,v in obj.items()}
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--minutes", type=float, default=0.05); ap.add_argument("--emulate", action="store_true")
    args=ap.parse_args(); args.out_dir.mkdir(parents=True, exist_ok=True)
    end=time.time()+args.minutes*60; idx=0
    while time.time()<end:
        rec=redact({"ts":datetime.now(timezone.utc).isoformat(),"tick":idx,
            "battery_pct": None if not args.emulate else max(5,100-idx),
            "thermal_c": None if not args.emulate else 35+(idx%7), "crash": False,
            "evidence_class": "SIMULATED" if args.emulate else "HARDWARE_PENDING"})
        p=args.out_dir/f"soak_{idx:05d}.json"; p.write_text(json.dumps(rec, indent=2))
        if idx%10==9:
            (args.out_dir/"integrity.log").open("a").write(f"{p.name} {hashlib.sha256(p.read_bytes()).hexdigest()}\n")
        idx+=1; time.sleep(0.05)
    (args.out_dir/"manifest.json").write_text(json.dumps({"ticks":idx,"mode":"emulate" if args.emulate else "hardware_pending"}, indent=2))
    print({"ticks":idx}); return 0
if __name__ == "__main__": raise SystemExit(main())
