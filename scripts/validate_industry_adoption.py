#!/usr/bin/env python3
"""Validate industry adoption registry against scoring schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
    import jsonschema
except ImportError:
    print("pyyaml and jsonschema required")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "program/industry_adoption/registry.yaml"
SCHEMA = ROOT / "program/industry_adoption/scoring.schema.json"

# Canonical shortlist (aliases accepted for naming variants)
REQUIRED_GROUPS = {
    "sionna": {"sionna", "nvidia_sionna"},
    "nyusim": {"nyusim"},
    "5g_lena_ns3": {"5g_lena_ns3", "fiveg_lena_ns3", "lena_ns3"},
    "oai_flexric": {"oai_flexric"},
    "oran_sc": {"oran_sc"},
    "open5gs": {"open5gs"},
    "camara": {"camara"},
    "opentelemetry": {"opentelemetry"},
    "grafana_oss": {"grafana_oss"},
    "zephyr": {"zephyr"},
    "mcuboot": {"mcuboot"},
    "tracy": {"tracy"},
    "openxr": {"openxr"},
    "vulkan": {"vulkan"},
    "webrtc": {"webrtc"},
    "catalogue_of_life": {"catalogue_of_life"},
    "gbif": {"gbif"},
    "smithsonian_oa": {"smithsonian_oa"},
    "godot": {"godot"},
}


def main() -> int:
    registry = yaml.safe_load(REG.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    resources = registry.get("resources") or []
    if not resources:
        print("INDUSTRY_ADOPTION_FAIL")
        print("- no resources")
        return 1
    errors = []
    for r in resources:
        try:
            jsonschema.validate(r, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{r.get('id')}: {exc.message}")
    ids = {r["id"] for r in resources}
    missing = []
    for canon, aliases in REQUIRED_GROUPS.items():
        if ids.isdisjoint(aliases):
            missing.append(canon)
    if missing:
        errors.append(f"missing shortlist resources: {sorted(missing)}")
    # Ensure decisions are only allowed enum values (already in schema)
    if errors:
        print("INDUSTRY_ADOPTION_FAIL")
        for e in errors:
            print("-", e)
        return 1
    print("INDUSTRY_ADOPTION_OK")
    print("resources=", len(ids))
    decisions = {}
    for r in resources:
        decisions.setdefault(r["decision"], []).append(r["id"])
    for d, items in sorted(decisions.items()):
        print(f"{d}: {', '.join(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
