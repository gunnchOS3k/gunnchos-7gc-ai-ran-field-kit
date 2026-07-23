"""Gate 1 locked thesis authority tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_gate1_thesis import evaluate  # noqa: E402


def test_gate1_validator_pass():
    result = evaluate()
    assert result["ok"] is True
    assert result["gate1_status"] == "GATE_1_PASS"


def test_exactly_one_title_and_hypothesis():
    payload = json.loads((ROOT / "contracts/gate1_locked_thesis.v1.json").read_text())
    assert payload["title"].startswith("Resilience-Aware, Human-Centric AI-RAN")
    assert "privacy-preserving orchestration architecture" in payload["central_hypothesis"]
    text = (ROOT / "GATE1_LOCKED_RESEARCH_THESIS.md").read_text()
    assert text.count(payload["title"]) >= 1
    assert text.count(payload["central_hypothesis"]) == 1


def test_exactly_three_rqs_and_papers():
    payload = json.loads((ROOT / "contracts/gate1_locked_thesis.v1.json").read_text())
    assert len(payload["research_questions"]) == 3
    assert len(payload["papers"]) == 3
    assert {q["id"] for q in payload["research_questions"]} == {"RQ1", "RQ2", "RQ3"}


def test_featured_repos_map_and_readygary_optional():
    payload = json.loads((ROOT / "contracts/gate1_locked_thesis.v1.json").read_text())
    by_name = {r["name"]: r for r in payload["repositories"]}
    for name in [
        "gunnchos-7gc-ai-ran-field-kit",
        "edge-io-measurement-node",
        "7gc-digital-twin",
        "spectrumx-ai-ran-gary",
        "ntn-resilience-sim",
    ]:
        assert by_name[name]["required"] is True
        assert by_name[name]["primary_questions"]
    assert by_name["readygary-6g-beam-selection"]["required"] is False
    assert by_name["readygary-6g-beam-selection"]["primary_questions"] == []
