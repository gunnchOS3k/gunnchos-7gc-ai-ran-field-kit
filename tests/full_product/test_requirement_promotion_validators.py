"""Validators for full-product requirement promotions and totality counters."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "program" / "full_product" / "requirement_graph.yaml"
RULES = ROOT / "program" / "full_product" / "promotion_rules.yaml"
VALIDATOR = ROOT / "scripts" / "validate_full_product_requirement_graph.py"
SYNC = ROOT / "scripts" / "sync_full_product_requirement_totality.py"


def test_graph_exists_and_has_status_fields():
    data = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    assert data["count"] == len(data["nodes"])
    assert data["unmapped_count"] == 0
    assert data["unowned_count"] == 0
    assert data["unclassified_count"] == 0
    for node in data["nodes"][:20]:
        assert node.get("ownership_status") == "OWNED"
        assert node.get("classification_status") == "CLASSIFIED"
        assert node.get("mapping_status") in {"MAPPED", "INGESTED", "COVERED"}


def test_validator_passes_current_graph():
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "FULL_PRODUCT_REQUIREMENT_GRAPH_PASS" in proc.stdout


def test_invalid_promotion_without_paths_fails(tmp_path: Path):
    data = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    # Corrupt one DOC_ONLY node into IMPLEMENTED without paths
    for node in data["nodes"]:
        if node["full_product_status"] == "DOC_ONLY":
            node["full_product_status"] = "IMPLEMENTED"
            node["implementation_paths"] = []
            node["tests"] = []
            node["evidence"] = []
            node["accepted_sha"] = None
            break
    data["status_counts"] = {}
    from collections import Counter

    data["status_counts"] = dict(Counter(n["full_product_status"] for n in data["nodes"]))
    bad = tmp_path / "bad_graph.yaml"
    bad.write_text(yaml.safe_dump(data), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--graph", str(bad)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "FULL_PRODUCT_REQUIREMENT_GRAPH_FAIL" in proc.stdout
    assert "implementation_paths" in proc.stdout


def test_honest_promotions_have_resolvable_paths():
    data = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    promoted = [
        n
        for n in data["nodes"]
        if n["full_product_status"] in {"IMPLEMENTED", "INTEGRATED", "DIGITALLY_VALIDATED"}
    ]
    assert promoted, "expected at least one honest promotion"
    for node in promoted:
        assert node.get("implementation_paths")
        assert node.get("tests")
        assert node.get("accepted_sha")
        assert node.get("evidence")
        for p in node["implementation_paths"]:
            assert (ROOT / p).exists(), p


def test_claim_firewall_script_exists_for_standards_promotion():
    assert (ROOT / "scripts" / "validate_claim_firewall.py").exists()
    assert (ROOT / "program" / "claims" / "prohibited_claim_patterns.yaml").exists()
