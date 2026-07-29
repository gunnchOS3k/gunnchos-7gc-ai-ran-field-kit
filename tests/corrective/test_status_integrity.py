"""Status-integrity tests: false PASS states must be rejected."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_corrective_validators import (  # noqa: E402
    validate_application_pack,
    validate_gate5_publication,
    validate_nvidia_aerial_depth,
    validate_oulu_scientific,
)
from verify_inherited_ci import evaluate  # noqa: E402


def test_oulu_smoke_without_causal_denies_scientific_pass():
    result = validate_oulu_scientific()
    assert result["status"] != "GATE4_OULU_SCIENTIFIC_EVIDENCE_PASS"
    assert result["ok"] is False


def test_educational_only_nvidia_denies_aerial_depth_pass():
    result = validate_nvidia_aerial_depth()
    assert result["status"] != "GATE4_NVIDIA_AERIAL_DEPTH_PASS"
    assert result.get("aerial_denied") is True or result["ok"] is False


def test_gate5_denies_without_figures_or_bibliography():
    result = validate_gate5_publication()
    assert result["status"] != "GATE5_RELEASE_CANDIDATE_PASS"
    assert result.get("independent_reproduction") == "GATE5_INDEPENDENT_REPRODUCTION_PENDING"
    assert result.get("doi_status") == "GATE5_DOI_PENDING"


def test_application_pack_rejects_absolute_path(tmp_path):
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "meta.json").write_text(json.dumps({"path": "/Users/gunnchos/secret"}))
    result = validate_application_pack(pack)
    assert result["ok"] is False
    assert any("absolute_local_path" in e for e in result["errors"])


def test_application_pack_rejects_null_commit(tmp_path):
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "meta.json").write_text('{"commit": null}')
    result = validate_application_pack(pack)
    assert result["ok"] is False
    assert any("commit_null" in e for e in result["errors"])


def test_inherited_ci_blocks_dependent_pass():
    status_map = {
        "gate2_integrated_system": "fail",
        "application_readiness": "pass",
        "gate4_oulu_scientific": "pass",
        "gate4_nvidia_aerial_depth": "pass",
        "gate5_publication_release": "pass",
        "gate6_harness": "pass",
        "repo_lock_clean": "pass",
    }
    graph = json.loads((ROOT / "STATUS_DEPENDENCY_GRAPH.json").read_text())
    result = evaluate(status_map, graph=graph)
    assert result["ok"] is False
    assert "gate4_oulu_scientific" in result["failures"]


def test_author_reproduction_not_independent():
    result = validate_gate5_publication()
    assert "INDEPENDENT_REPRODUCTION_PENDING" in result["independent_reproduction"]


def test_still_running_blocks_release():
    status_map = {
        "gate2_integrated_system": "pass",
        "application_readiness": "pass",
        "gate4_oulu_scientific": "running",
        "gate4_nvidia_aerial_depth": "pass",
        "gate5_publication_release": "pass",
        "gate6_harness": "pass",
        "repo_lock_clean": "pass",
    }
    graph = json.loads((ROOT / "STATUS_DEPENDENCY_GRAPH.json").read_text())
    result = evaluate(status_map, graph=graph)
    assert result["ok"] is False
    assert "gate5_publication_release" in result["failures"]
