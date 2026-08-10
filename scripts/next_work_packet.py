#!/usr/bin/env python3
"""Print next READY work packet under WIP limits (Operating Cycle model)."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
active = json.loads((ROOT/"program/operating_model/ACTIVE_WIP.json").read_text())
backlog = json.loads((ROOT/"program/operating_model/13_BOOTSTRAP/INITIAL_CANONICAL_BACKLOG.json").read_text())
print("ACTIVE:", ",".join(active.get("active") or []))
print("WIP_LIMIT:", active.get("MAX_ACTIVE_MAJOR_WORKSTREAMS"))
ready=[i for i in backlog.get("items") or [] if i.get("status")=="READY" and i.get("id") not in (active.get("active") or [])]
ready.sort(key=lambda x: -int(x.get("priority_score") or 0))
print("NEXT_READY_AFTER_CYCLE:")
for i in ready[:5]:
    print(f"  {i['id']} score={i.get('priority_score')} {i.get('title')}")
