"""External registry tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from register_external_dataset import default_registry, verify_registry, register  # noqa: E402


def test_registry_requires_license():
    register()
    result = verify_registry()
    assert result["ok"]
    reg = json.loads((ROOT / "datasets/external/registry/external_dataset_registry.json").read_text())
    for rec in reg["records"]:
        assert rec["license_or_terms"]


def test_missing_license_fails(tmp_path, monkeypatch):
    bad = default_registry()
    bad["records"][0]["license_or_terms"] = ""
    path = ROOT / "datasets/external/registry/external_dataset_registry.json"
    path.write_text(json.dumps(bad, indent=2))
    result = verify_registry()
    assert not result["ok"]
    # restore
    path.write_text(json.dumps(default_registry(), indent=2) + "\n")
