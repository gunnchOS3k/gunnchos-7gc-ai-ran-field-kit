#!/usr/bin/env python3
"""Lightweight license-boundary checks for industry adoption adapters."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = ROOT / "program/industry_adoption/license_boundaries.yaml"
ADAPTER_ROOT = ROOT / "industry_research_stack/adapters"

# Product-link forbidden markers for GPL/AGPL adapters
FORBIDDEN_PHRASES = (
    "linked_into_product\": True",
    "embedded_in_product\": True",
    "linked_into_product: true",
    "embedded_in_product: true",
)


def main() -> int:
    data = yaml.safe_load(BOUNDARIES.read_text(encoding="utf-8"))
    errors = []
    if "gplv2" not in (data.get("rules") or {}):
        errors.append("missing gplv2 rule")
    if "agplv3" not in (data.get("rules") or {}):
        errors.append("missing agplv3 rule")
    if "oai_cssl" not in (data.get("rules") or {}):
        errors.append("missing oai_cssl rule")
    for path in ADAPTER_ROOT.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                errors.append(f"{path.name} claims product link/embed: {phrase}")
    # Grafana TEST_ONLY note expected in notes or reports
    notes = data.get("notes") or {}
    if "grafana" not in str(notes).lower() and "grafana" not in BOUNDARIES.read_text().lower():
        report = ROOT / "program/industry_adoption/reports/LICENSE_AND_IP_BOUNDARY_REPORT.md"
        if not report.exists() or "Grafana" not in report.read_text():
            errors.append("Grafana TEST_ONLY boundary note missing")
    if errors:
        print("INDUSTRY_LICENSE_BOUNDARIES_FAIL")
        for e in errors:
            print("-", e)
        return 1
    print("INDUSTRY_LICENSE_BOUNDARIES_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
