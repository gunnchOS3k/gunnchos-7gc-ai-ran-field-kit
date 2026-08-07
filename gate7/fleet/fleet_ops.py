#!/usr/bin/env python3
"""Local/dev fleet operations software."""
from __future__ import annotations
import argparse, json, uuid
from pathlib import Path
from datetime import datetime, timezone
class Fleet:
    def __init__(self): self.devices={}
    def enroll(self, site: str) -> dict:
        did=str(uuid.uuid4())
        rec={"device_id":did,"site":site,"health":"unknown","wave":None,"quarantine":False,
             "ts":datetime.now(timezone.utc).isoformat()}
        self.devices[did]=rec; return rec
    def set_health(self, did, health): self.devices[did]["health"]=health
    def rollout(self, wave, ids):
        for did in ids: self.devices[did]["wave"]=wave
    def quarantine(self, did, reason):
        self.devices[did]["quarantine"]=True; self.devices[did]["quarantine_reason"]=reason
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out", type=Path, required=True); args=ap.parse_args()
    f=Fleet(); d1=f.enroll("lab-dev"); d2=f.enroll("lab-dev")
    f.set_health(d1["device_id"],"ok"); f.rollout("wave-0-dev",[d1["device_id"],d2["device_id"]])
    f.quarantine(d2["device_id"],"simulated_anomaly")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"devices":list(f.devices.values()),"mode":"local-dev"}, indent=2))
    print("enrolled", len(f.devices)); return 0
if __name__ == "__main__": raise SystemExit(main())
