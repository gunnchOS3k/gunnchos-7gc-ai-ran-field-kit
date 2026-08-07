#!/usr/bin/env python3
"""Fetch authoritative standards pages; emit machine-readable delta."""
from __future__ import annotations
import hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
STD = ROOT / "standards"
URLS = {
  "ITU-IMT-2030": "https://www.itu.int/en/ITU-R/study-groups/rsg5/rwp5d/imt-2030/pages/default.aspx",
  "ITU-IMT-FAMILY": "https://www.itu.int/en/ITU-R/study-groups/rsg5/rwp5d/pages/imt.aspx",
  "3GPP-REL20": "https://www.3gpp.org/specifications-technologies/releases/release-20",
}
def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "gunnchos-standards-watch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    return hashlib.sha256(data).hexdigest()
def main() -> int:
    out_dir = STD / "watch" / "out"; out_dir.mkdir(parents=True, exist_ok=True)
    prev_path = out_dir / "last_hashes.json"
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    current = {}; deltas = []
    for sid, url in URLS.items():
        try:
            h = fetch(url); status = "ok"
        except Exception as e:
            h, status = None, f"error:{e}"
        current[sid] = {"url": url, "sha256": h, "status": status}
        old = prev.get(sid, {}).get("sha256")
        if h and old and h != old:
            deltas.append({"source": sid, "change": "hash_changed", "old": old, "new": h})
        elif h and not old:
            deltas.append({"source": sid, "change": "baseline_or_first_seen", "new": h})
    report = {"generated_at": now, "current": current, "deltas": deltas,
              "compliance_claim": "NONE — do not auto-claim compliance after source change"}
    (out_dir / f"watch_report_{now}.json").write_text(json.dumps(report, indent=2))
    prev_path.write_text(json.dumps(current, indent=2))
    print(json.dumps({"deltas": len(deltas), "status": "WATCH_OK"}, indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
