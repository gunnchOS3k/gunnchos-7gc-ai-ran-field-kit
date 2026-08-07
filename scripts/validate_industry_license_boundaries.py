#!/usr/bin/env python3
"""Validate industry license boundaries and adapter provenance (not legal certification)."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "program/industry_adoption/registry.yaml"
BOUNDARIES = ROOT / "program/industry_adoption/license_boundaries.yaml"
ADAPTERS = ROOT / "industry_research_stack/adapters"

GPL = {"GPL-2.0", "GPL-2.0-only", "GPL-2.0-or-later"}
AGPL = {"AGPL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later"}
PRODUCT_LINK_FORBIDDEN = {"TEST_ONLY"}


def main() -> int:
    errors: list[str] = []
    reg = yaml.safe_load(REGISTRY.read_text())
    bounds = yaml.safe_load(BOUNDARIES.read_text())
    if not bounds.get("rules"):
        errors.append("license_boundaries.yaml missing rules")

    for res in reg.get("resources", []):
        decision = res["decision"]
        lic = str(res.get("license", ""))
        rid = res["id"]
        if any(g in lic for g in GPL) and decision == "ADOPT":
            errors.append(f"{rid}: GPLv2 marked ADOPT — must be TEST_ONLY/external unless deliberate licensing decision")
        if any(a in lic for a in AGPL) and decision == "ADOPT":
            errors.append(f"{rid}: AGPLv3 marked ADOPT — must be TEST_ONLY standalone unless compliance decision")
        if decision in ("ADOPT", "ADAPT_INTERFACE") and not res.get("requirement_ids"):
            errors.append(f"{rid}: ADOPT/ADAPT without requirement_ids")

    # Flat ToolAdapter modules (preferred) OR package dirs with manifest.yaml
    skip_dirs = {"__pycache__", "fixtures", "tests"}
    flat_modules = {
        "sionna": "sionna.py",
        "nyusim": "nyusim.py",
        "lena_ns3": "lena_ns3.py",
        "oai_flexric": "oai_flexric.py",
        "oran_sc": "oran_sc.py",
        "open5gs": "open5gs.py",
        "camara": "camara.py",
    }
    for name, fname in flat_modules.items():
        py = ADAPTERS / fname
        if not py.exists():
            errors.append(f"missing adapter module: {fname}")
            continue
        text = py.read_text(encoding="utf-8")
        for needle in ("license", "source_url", "pinned_version"):
            if needle not in text:
                errors.append(f"{fname}: missing {needle} field in adapter class")

    for adapter_dir in sorted(ADAPTERS.glob("*")):
        if not adapter_dir.is_dir() or adapter_dir.name in skip_dirs:
            continue
        man = adapter_dir / "manifest.yaml"
        if not man.exists():
            # Package without manifest is only OK if mirrored by flat module
            if adapter_dir.name not in flat_modules and not (ADAPTERS / f"{adapter_dir.name}.py").exists():
                errors.append(f"missing manifest: {adapter_dir}")
            continue
        m = yaml.safe_load(man.read_text())
        for key in ("pinned_version", "license", "source_url", "decision", "provenance_required"):
            if key not in m:
                errors.append(f"{adapter_dir.name}: missing {key}")
        py = adapter_dir / "adapter.py"
        if not py.exists():
            errors.append(f"{adapter_dir.name}: missing adapter.py")

    if errors:
        print("LICENSE_BOUNDARY_FAIL")
        for e in errors:
            print(f" - {e}")
        return 1
    print("LICENSE_BOUNDARY_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
