"""Validators for full-product requirement promotions and totality counters."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SIBLING = ROOT.parent
GRAPH = ROOT / "program" / "full_product" / "requirement_graph.yaml"
RULES = ROOT / "program" / "full_product" / "promotion_rules.yaml"
VALIDATOR = ROOT / "scripts" / "validate_full_product_requirement_graph.py"


def _resolve(raw: str) -> Path:
    if raw.startswith("sibling:"):
        return SIBLING / raw[len("sibling:") :]
    return ROOT / raw


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
        [sys.executable, str(VALIDATOR), "--strict-totality"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "FULL_PRODUCT_REQUIREMENT_GRAPH_PASS" in proc.stdout


def test_invalid_promotion_without_paths_fails(tmp_path: Path):
    data = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    # Corrupt a non-higher node into IMPLEMENTED without Cont IV proof fields
    corrupted = False
    for node in data["nodes"]:
        if node["full_product_status"] in {
            "DOC_ONLY",
            "SCHEMA_ONLY",
            "STUB_ONLY",
            "PHYSICAL_REQUIRED",
            "EXTERNAL_REQUIRED",
        }:
            node["full_product_status"] = "IMPLEMENTED"
            node["implementation_paths"] = []
            node["test_paths"] = []
            node["tests"] = []
            node["evidence"] = []
            node["accepted_sha"] = None
            node["accepted_main_sha"] = None
            node["accepted_repository"] = None
            node["evidence_artifact"] = None
            node["evidence_result"] = None
            corrupted = True
            break
    assert corrupted, "expected a node available to corrupt for negative test"
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
        assert node.get("test_paths") or node.get("tests")
        assert node.get("accepted_main_sha") or node.get("accepted_sha")
        assert node.get("accepted_repository")
        assert node.get("evidence_artifact")
        assert node.get("evidence_result")
        assert node.get("evidence") or node.get("evidence_artifact")
        for p in node["implementation_paths"]:
            assert _resolve(p).exists(), p


def test_no_doc_only_residual_after_cont_iv():
    data = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    doc_only = [n["id"] for n in data["nodes"] if n["full_product_status"] == "DOC_ONLY"]
    assert doc_only == [], f"Cont IV must move digitally provable nodes out of DOC_ONLY: {doc_only[:10]}"


def test_claim_firewall_script_exists_for_standards_promotion():
    assert (ROOT / "scripts" / "validate_claim_firewall.py").exists()
    assert (ROOT / "program" / "claims" / "prohibited_claim_patterns.yaml").exists()


def test_cont_iv_proof_reports_exist():
    reports = ROOT / "program" / "full_product" / "reports"
    assert (reports / "REQUIREMENT_PROOF_LEDGER.md").exists()
    assert (reports / "REQUIREMENT_PROOF_COUNTS.json").exists()
    assert (reports / "REQUIREMENT_PROOF_GAPS.md").exists()
    assert (reports / "CONTINUATION_IV_ACCEPTED_BASELINE.md").exists()
