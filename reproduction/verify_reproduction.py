#!/usr/bin/env python3
from pathlib import Path
import sys
REQUIRED = [
  '01_edge_measurements.json','02_twin_state.json','03_airan_twin_informed_decision.json',
  '04_resilience_decision.json','manifest.json','checksums.sha256','gate2_status.json'
]
run_dir = Path(sys.argv[1])
missing = [r for r in REQUIRED if not (run_dir/r).is_file()]
if missing:
    raise SystemExit('missing: '+', '.join(missing))
print('reproduction artifacts present')
