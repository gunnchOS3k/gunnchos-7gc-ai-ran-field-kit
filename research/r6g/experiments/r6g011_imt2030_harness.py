"""R6G-011 — IMT-2030 independent evaluation harness map (digital).

Never emits STANDARDIZED_6G / COMPLIANT without official evidence.
Official TPR numerics remain OFFICIAL_VALUE_PENDING until unrestricted Doc 5/116.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import assert_no_soa

ROOT = Path(__file__).resolve().parents[3]
TPR_PATH = ROOT / "standards" / "imt2030" / "technical_performance_requirements.json"


def run_r6g011() -> dict[str, Any]:
    tpr = json.loads(TPR_PATH.read_text(encoding="utf-8"))
    reqs = tpr.get("requirements", [])
    pending = sum(1 for r in reqs if r.get("official_value") == "OFFICIAL_VALUE_PENDING")
    boundary = tpr.get("claim_boundary", {})
    packet_map = {
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
    report = {
        "schema": "gunnchos.r6g.r6g011.v1",
        "packet": "R6G-011",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "claim_state": "MODELED",
        "imt2030_tpr_source": str(TPR_PATH.relative_to(ROOT)),
        "requirement_count": len(reqs),
        "official_value_pending_count": pending,
        "all_official_values_pending": pending == len(reqs) and len(reqs) > 0,
        "packet_to_imt2030_scenarios": packet_map,
        "claim_boundary": {
            "STANDARDIZED_6G": False,
            "COMPLIANT": False,
            "6G_CERTIFIED": False,
            "CARRIER_ACCEPTED": False,
            "GATE_8_PASS": False,
            "source_boundary_STANDARDIZED_6G": boundary.get("STANDARDIZED_6G", False),
        },
        "evaluation_methods_allowed": ["SIMULATION", "ANALYTICAL", "INSPECTION"],
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "note": (
            "Harness maps packets to IMT-2030 scenarios; never STANDARDIZED_6G/COMPLIANT "
            "while official_value=OFFICIAL_VALUE_PENDING."
        ),
    }
    assert_no_soa(report)
    assert report["claim_boundary"]["STANDARDIZED_6G"] is False
    assert report["claim_boundary"]["COMPLIANT"] is False
    return report
