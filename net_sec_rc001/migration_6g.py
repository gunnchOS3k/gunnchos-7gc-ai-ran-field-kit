"""6G migration abstraction + standards delta ingestion."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def ingest_standards_delta() -> dict[str, Any]:
    rel = json.loads((ROOT / "standards" / "3gpp" / "release_tracker.json").read_text(encoding="utf-8"))
    tpr = json.loads(
        (ROOT / "standards" / "imt2030" / "technical_performance_requirements.json").read_text(encoding="utf-8")
    )
    pending_values = sum(1 for r in tpr["requirements"] if r["official_value"] == "OFFICIAL_VALUE_PENDING")
    return {
        "rel20_status": rel["release_20"]["status"],
        "rel21_status": rel["release_21"]["status"],
        "rel21_freeze_claimed": rel["release_21"]["freeze_claimed"],
        "tpr_count": tpr["requirement_count"],
        "official_value_pending_count": pending_values,
        "STANDARDIZED_6G": False,
    }


def run_migration_abstraction() -> dict[str, Any]:
    delta = ingest_standards_delta()
    abstraction = {
        "replaceable_wwan": True,
        "software_defined_policy": True,
        "future_ran_core_hooks": ["radio_capability_provider", "core_amf_stub", "ntn_sim_adapter"],
        "normative_6g_specs": "NOT_YET",
    }
    ok = (
        delta["rel21_freeze_claimed"] is False
        and delta["STANDARDIZED_6G"] is False
        and delta["official_value_pending_count"] == 20
        and abstraction["normative_6g_specs"] == "NOT_YET"
    )
    return {
        "schema": "gunnchos.net_sec_rc001.migration_6g.v1",
        "ok": ok,
        "delta": delta,
        "abstraction": abstraction,
        "product_wording": (
            "Software-defined architecture engineered for 5G-Advanced and NTN-capable "
            "paths (NTN via simulation), IMT-2030-aligned, and engineered for migration "
            "to standardized 6G; Quectel RM520N-GL digital baseline is Rel-16 NSA+SA "
            "Sub-6 terrestrial only — not 5G-Advanced hardware and not NTN."
        ),
        "STANDARDIZED_6G": False,
        "6G_CERTIFIED": False,
        "GATE_8_PASS": False,
        "token_candidates": [
            "REL20_REL21_MIGRATION_TRACKER",
            "IMT2030_MAPPING_COMPLETE_CURRENT_PUBLIC_DRAFT",
        ],
    }
