"""Additive closed-loop V2 contract tests. Existing V1 tests stay intact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from control_plane.actuation_firewall import evaluate_request, real_actuation_enabled
from control_plane.campus_catalog import CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256, SITE_IDS
from control_plane.closed_loop import run_seven_campus_loop
from control_plane.ric_adapters import (
    OAIAdapter,
    ORANSCAdapter,
    ReadOnlyTelemetryAdapter,
    SimulatedRICAdapter,
    SrsRANAdapter,
)
from validate_contract import ContractError, validate_document

SCHEMA = ROOT / "contracts"


def test_new_valid_fixtures_pass():
    for name in [
        "campus_design_bundle.valid.json",
        "campus_optimization_result.valid.json",
        "twin_calibration_bundle.valid.json",
        "ran_actuation_request.valid.json",
        "ran_actuation_receipt.valid.json",
        "campus_measurement_mapping.valid.json",
    ]:
        path = ROOT / "fixtures/valid" / name
        doc = json.loads(path.read_text())
        validate_document(doc, SCHEMA, enforce_privacy=True)


@pytest.mark.parametrize("family", ["campus", "optimization", "calibration", "actuation"])
def test_new_invalid_families_fail(family: str):
    files = sorted((ROOT / f"fixtures/invalid/{family}").glob("*.json"))
    assert len(files) >= 5
    for path in files:
        doc = json.loads(path.read_text())
        with pytest.raises(ContractError):
            validate_document(doc, SCHEMA, enforce_privacy=True)


def test_new_invalid_have_reasons():
    for family in ["campus", "optimization", "calibration", "actuation"]:
        for path in (ROOT / f"fixtures/invalid/{family}").glob("*.json"):
            reason = path.with_suffix(".reason.txt")
            assert reason.is_file()
            assert reason.read_text().strip()


def test_seven_campus_closed_loop():
    report = run_seven_campus_loop()
    assert report["SYNTHETIC_CLOSED_LOOP_PASS"] == "7/7"
    assert report["SEVEN_CAMPUS_BACKEND_PASS"] == "7/7"
    assert report["MLV_V2_SOURCE_HASH_COMPAT_PASS"] is True
    assert report["source_manifest_sha256"] == CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256
    assert report["campuses"] == list(SITE_IDS)
    for result in report["results"]:
        validate_document(result["design"], SCHEMA, enforce_privacy=True)
        validate_document(result["twin"], SCHEMA, enforce_privacy=True)
        validate_document(result["optimization"], SCHEMA, enforce_privacy=True)
        validate_document(result["calibration"], SCHEMA, enforce_privacy=True)
        validate_document(result["mapping"], SCHEMA, enforce_privacy=True)
        validate_document(result["actuation_request"], SCHEMA, enforce_privacy=True)
        validate_document(result["actuation_receipt"], SCHEMA, enforce_privacy=True)
        assert result["design"]["geometry_fidelity"] == "AUTHORED_PLANNING_LAYOUT"
        assert result["twin"]["service_demand"]["values"]["geometry_fidelity"] == (
            "AUTHORED_PLANNING_LAYOUT"
        )
        assert result["calibration"]["new_model_version"] != result["calibration"]["parent_model_version"]
        assert result["actuation_receipt"]["applied"] is False
        assert result["actuation_receipt"]["e2_claimed"] is False
        assert result["mapping"]["contains_person_path"] is False
        assert result["mapping"]["exact_minor_location"] is False
        if result["site_id"] == "gaza":
            assert result["design"]["privacy"]["location_precision"] == "abstract_zone"
            assert result["design"]["privacy"]["gaza_sensitive_export"] is False
        if result["site_id"] == "graham_land":
            assert result["design"]["privacy"]["graham_station_claim"] is False


def test_read_only_ric_refuses_actuation():
    adapter = ReadOnlyTelemetryAdapter()
    receipt = adapter.actuate(
        json.loads((ROOT / "fixtures/valid/ran_actuation_request.valid.json").read_text())
    )
    assert receipt["applied"] is False
    assert receipt["decision"] == "denied"
    sim = SimulatedRICAdapter()
    rec = sim.recommend({"site_id": "gary"})
    assert rec["e2_claimed"] is False
    assert real_actuation_enabled() is False


def test_optional_ran_backends_fail_closed():
    for adapter in (SrsRANAdapter(), OAIAdapter(), ORANSCAdapter()):
        with pytest.raises(RuntimeError):
            adapter.actuate({"run_id": "x"})


def test_browser_direct_denied_by_firewall():
    request = json.loads((ROOT / "fixtures/valid/ran_actuation_request.valid.json").read_text())
    request["source_path"] = "browser"
    receipt = evaluate_request(request)
    assert receipt["applied"] is False
    assert receipt["decision"] == "denied"
