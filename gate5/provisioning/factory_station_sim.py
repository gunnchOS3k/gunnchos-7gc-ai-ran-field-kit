#!/usr/bin/env python3
"""Local provisioning station simulator — DEV keys only."""
from __future__ import annotations
import argparse, json, hashlib, uuid
from pathlib import Path
from datetime import datetime, timezone
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out", type=Path, required=True); args=ap.parse_args()
    serial=f"DEV-{uuid.uuid4().hex[:12]}"; digest=hashlib.sha256(b"dev-image").hexdigest()
    rec={"device_id":str(uuid.uuid4()),"serial":serial,"key_realm":"DEV","image_digest":digest,
         "cert_pem":"DEV_CERT_PLACEHOLDER","station_id":"local-sim-01","result":"PASS",
         "ts":datetime.now(timezone.utc).isoformat(),
         "note":"Not a production factory image; DEV keys only"}
    args.out.parent.mkdir(parents=True, exist_ok=True); args.out.write_text(json.dumps(rec, indent=2))
    print(rec["serial"], rec["result"]); return 0
if __name__ == "__main__": raise SystemExit(main())
