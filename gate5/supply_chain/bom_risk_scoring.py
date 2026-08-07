#!/usr/bin/env python3
"""Score APL candidate risks; never invent prices."""
from __future__ import annotations
import csv, json
from pathlib import Path
def score_row(r: dict) -> dict:
    risk = 0
    risk += {"high":3,"medium":2,"low":1}.get(r.get("single_source_risk",""),0)
    if r.get("quote_status") == "LIVE_QUOTE_REQUIRED": risk += 1
    if r.get("lifecycle") in {"unknown","nrnd","obsolete"}: risk += 2
    if r.get("security_sensitive") == "yes": risk += 1
    return {"part_id": r["part_id"], "risk_score": risk, "quote_status": r.get("quote_status")}
def main() -> int:
    src = Path(__file__).with_name("approved_parts_list_candidate.csv")
    rows = list(csv.DictReader(src.open()))
    out = [score_row(r) for r in rows]
    Path(__file__).with_name("bom_risk_report.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
