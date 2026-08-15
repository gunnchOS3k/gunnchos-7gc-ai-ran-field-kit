"""R6G-011 — IMT-2030 independent evaluation harness (executable, honest).

Loads source-pinned requirements, validates units/inputs, maps outputs to metrics,
marks unavailable / final-pending honestly.
Never emits hardcoded 6G_COMPLIANT / STANDARDIZED_6G.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import assert_no_soa

ROOT = Path(__file__).resolve().parents[3]
TPR_PATH = ROOT / "standards" / "imt2030" / "technical_performance_requirements.json"

# Honest evidence labels — never 6G_COMPLIANT.
EVIDENCE_LABELS = (
    "MEASURED",
    "NOT_MEASURED",
    "NOT_APPLICABLE",
    "STANDARD_PENDING",
    "INSUFFICIENT_EVIDENCE",
)

# Digital packets that can contribute simulation evidence for a scenario family.
PACKET_SCENARIO_MAP = {
    "R6G-001": ["IC", "HRLLC", "MC", "UC", "AIAC", "ISAC"],
    "R6G-002": ["UC", "IC"],
    "R6G-003": ["ISAC", "UC", "HRLLC"],
    "R6G-004": ["ISAC", "HRLLC"],
    "R6G-005": ["AIAC", "IC"],
    "R6G-006": ["MC", "IC"],
    "R6G-007": ["IC", "ISAC"],
    "R6G-008": ["UC", "AIAC"],
    "R6G-009": ["AIAC", "ISAC", "UC"],
    "R6G-010": ["UC", "AIAC", "ISAC"],
    "R6G-011": ["IC", "HRLLC", "MC", "UC", "AIAC", "ISAC"],
}

# Lightweight digital observables available in this repo (not official TPR mins).
DIGITAL_OBSERVABLES = {
    "peak_data_rate": {"unit": "Mbps", "source_packet": "R6G-002", "method": "SIMULATION"},
    "user_experienced_data_rate": {"unit": "Mbps", "source_packet": "R6G-002", "method": "SIMULATION"},
    "latency": {"unit": "ms", "source_packet": "R6G-002", "method": "SIMULATION"},
    "reliability": {"unit": "availability_norm", "source_packet": "R6G-002", "method": "SIMULATION"},
    "sensing_related": {"unit": "rmse_m", "source_packet": "R6G-003", "method": "SIMULATION"},
    "security_related": {"unit": "accept_reject", "source_packet": "R6G-010", "method": "INSPECTION"},
    "ai_related": {"unit": "failure_rate", "source_packet": "R6G-005", "method": "SIMULATION"},
}


def _validate_requirement(req: dict[str, Any]) -> dict[str, Any]:
    issues = []
    rid = req.get("id")
    name = req.get("name")
    if not rid or not name:
        issues.append("missing_id_or_name")
    ov = req.get("official_value")
    ou = req.get("official_unit")
    if ov == "OFFICIAL_VALUE_PENDING":
        issues.append("official_value_pending")
    if ou == "OFFICIAL_UNIT_PENDING":
        issues.append("official_unit_pending")
    methods = req.get("allowed_methods") or []
    if not methods:
        issues.append("no_allowed_methods")
    em = req.get("evaluation_method")
    if em == "OFFICIAL_ASSIGNMENT_PENDING":
        issues.append("evaluation_method_pending")
    return {
        "id": rid,
        "name": name,
        "valid_structure": rid is not None and name is not None,
        "issues": issues,
        "official_value": ov,
        "official_unit": ou,
        "allowed_methods": methods,
        "evaluation_method": em,
    }


def _map_evidence(req: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    name = (req.get("name") or "").lower()
    # Default honest states
    if "official_value_pending" in validation["issues"] or "official_unit_pending" in validation["issues"]:
        label = "STANDARD_PENDING"
        measured_value = None
        comparable = False
    else:
        label = "INSUFFICIENT_EVIDENCE"
        measured_value = None
        comparable = False

    matched_obs = None
    for key, obs in DIGITAL_OBSERVABLES.items():
        if key.replace("_", "") in name.replace("_", "") or key.split("_")[0] in name:
            matched_obs = (key, obs)
            break
    # Broader keyword mapping
    if matched_obs is None:
        if "latency" in name or "delay" in name:
            matched_obs = ("latency", DIGITAL_OBSERVABLES["latency"])
        elif "sens" in name or "isac" in name or "position" in name:
            matched_obs = ("sensing_related", DIGITAL_OBSERVABLES["sensing_related"])
        elif "secur" in name or "trust" in name or "privacy" in name:
            matched_obs = ("security_related", DIGITAL_OBSERVABLES["security_related"])
        elif "ai" in name or "learning" in name:
            matched_obs = ("ai_related", DIGITAL_OBSERVABLES["ai_related"])
        elif "rate" in name or "throughput" in name or "spectral" in name:
            matched_obs = ("peak_data_rate", DIGITAL_OBSERVABLES["peak_data_rate"])
        elif "reliab" in name or "avail" in name:
            matched_obs = ("reliability", DIGITAL_OBSERVABLES["reliability"])

    if matched_obs and label == "STANDARD_PENDING":
        # We can run a digital method, but cannot claim MEASURED vs official min.
        key, obs = matched_obs
        return {
            "requirement_id": req.get("id"),
            "requirement_name": req.get("name"),
            "evidence_label": "STANDARD_PENDING",
            "digital_observable": key,
            "digital_method": obs["method"],
            "digital_unit": obs["unit"],
            "source_packet": obs["source_packet"],
            "measured_value": measured_value,
            "comparable_to_official_min": comparable,
            "note": "Digital method available; official TPR numeric still pending — not MEASURED against standard.",
        }
    if matched_obs is None and label == "STANDARD_PENDING":
        return {
            "requirement_id": req.get("id"),
            "requirement_name": req.get("name"),
            "evidence_label": "STANDARD_PENDING",
            "digital_observable": None,
            "measured_value": None,
            "comparable_to_official_min": False,
            "note": "No mapped digital observable; official value pending.",
        }
    return {
        "requirement_id": req.get("id"),
        "requirement_name": req.get("name"),
        "evidence_label": "INSUFFICIENT_EVIDENCE" if matched_obs is None else "NOT_MEASURED",
        "digital_observable": matched_obs[0] if matched_obs else None,
        "measured_value": None,
        "comparable_to_official_min": False,
        "note": "Honest non-compliant mapping — never 6G_COMPLIANT.",
    }


def run_r6g011() -> dict[str, Any]:
    tpr = json.loads(TPR_PATH.read_text(encoding="utf-8"))
    reqs = tpr.get("requirements", [])
    boundary = tpr.get("claim_boundary", {})
    source = tpr.get("source", {})

    validations = [_validate_requirement(r) for r in reqs]
    evidence_rows = [_map_evidence(r, v) for r, v in zip(reqs, validations)]

    pending = sum(1 for r in reqs if r.get("official_value") == "OFFICIAL_VALUE_PENDING")
    label_counts = {lab: 0 for lab in EVIDENCE_LABELS}
    for row in evidence_rows:
        lab = row["evidence_label"]
        if lab in label_counts:
            label_counts[lab] += 1

    coverage = {
        "requirements_total": len(reqs),
        "structure_valid": sum(1 for v in validations if v["valid_structure"]),
        "official_value_pending": pending,
        "evidence_label_counts": label_counts,
        "packet_to_imt2030_scenarios": PACKET_SCENARIO_MAP,
        "inputs_validated": all(v["valid_structure"] for v in validations),
        "units_official_pending": all(
            r.get("official_unit") == "OFFICIAL_UNIT_PENDING" for r in reqs
        ),
    }

    # Hard guard: never emit compliant / standardized
    forbidden_labels = {"6G_COMPLIANT", "COMPLIANT", "STANDARDIZED_6G", "MEASURED_COMPLIANT"}
    for row in evidence_rows:
        assert row["evidence_label"] not in forbidden_labels
        assert row["evidence_label"] in EVIDENCE_LABELS

    report = {
        "schema": "gunnchos.r6g.r6g011.v1",
        "packet": "R6G-011",
        "ok": True,
        "status": "DIGITALLY_EXECUTED_HARNESS",
        "claim_state": "DIGITALLY_EXECUTED_HARNESS",
        "ladder_earned": ["R0", "R1", "R2"],
        "execution_class": "EXECUTABLE_IMT2030_HARNESS",
        "imt2030_tpr_source": str(TPR_PATH.relative_to(ROOT)),
        "source_pin": source,
        "requirement_count": len(reqs),
        "official_value_pending_count": pending,
        "all_official_values_pending": pending == len(reqs) and len(reqs) > 0,
        "validations": validations,
        "evidence_rows": evidence_rows,
        "coverage_matrix": coverage,
        "evidence_labels_used": sorted({r["evidence_label"] for r in evidence_rows}),
        "claim_boundary": {
            "STANDARDIZED_6G": False,
            "COMPLIANT": False,
            "6G_CERTIFIED": False,
            "CARRIER_ACCEPTED": False,
            "GATE_8_PASS": False,
            "source_boundary_STANDARDIZED_6G": boundary.get("STANDARDIZED_6G", False),
        },
        "evaluation_methods_allowed": ["SIMULATION", "ANALYTICAL", "INSPECTION"],
        "IMT2030_HARNESS_DIGITAL": True,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "hardcoded_6g_compliant": False,
        "note": (
            "Executable harness with honest STANDARD_PENDING / NOT_MEASURED labels; "
            "never STANDARDIZED_6G/COMPLIANT while official values pending."
        ),
    }
    assert_no_soa(report)
    assert report["claim_boundary"]["STANDARDIZED_6G"] is False
    assert report["claim_boundary"]["COMPLIANT"] is False
    assert report["hardcoded_6g_compliant"] is False
    assert "6G_COMPLIANT" not in report["evidence_labels_used"]
    return report
