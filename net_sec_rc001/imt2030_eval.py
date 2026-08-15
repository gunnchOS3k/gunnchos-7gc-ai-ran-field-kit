"""IMT-2030 evaluation harness — per-requirement evidence states only."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_STATES = {
    "REQUIREMENT_EVALUATED",
    "NOT_YET_EVALUATABLE",
    "STANDARD_PENDING",
}


def run_imt2030_eval_harness() -> dict[str, Any]:
    tpr = json.loads(
        (ROOT / "standards" / "imt2030" / "technical_performance_requirements.json").read_text(encoding="utf-8")
    )
    envs = json.loads(
        (ROOT / "standards" / "imt2030" / "test_environments.json").read_text(encoding="utf-8")
    )
    methods = json.loads(
        (ROOT / "standards" / "imt2030" / "evaluation_methods.json").read_text(encoding="utf-8")
    )
    scenarios = json.loads(
        (ROOT / "standards" / "imt2030" / "usage_scenarios.json").read_text(encoding="utf-8")
    )

    per_req = []
    for req in tpr["requirements"]:
        state = req.get("evidence_state", "STANDARD_PENDING")
        assert state in ALLOWED_STATES
        # Until official values exist, harness marks STANDARD_PENDING / NOT_YET_EVALUATABLE.
        if req["official_value"] == "OFFICIAL_VALUE_PENDING":
            state = "STANDARD_PENDING"
        per_req.append({
            "id": req["id"],
            "name": req["name"],
            "evaluation_method": req["evaluation_method"],
            "evidence_state": state,
            "official_value": req["official_value"],
        })

    env_report = []
    for env in envs["environments"]:
        env_report.append({
            "id": env["id"],
            "usage_scenarios": env["usage_scenarios"],
            "params_status": env["params_status"],
            "evidence_state": "NOT_YET_EVALUATABLE" if env["params_status"] == "OFFICIAL_PARAMS_PENDING" else "REQUIREMENT_EVALUATED",
        })

    ok = (
        len(per_req) == 20
        and all(r["evidence_state"] in ALLOWED_STATES for r in per_req)
        and all(r["evidence_state"] != "REQUIREMENT_EVALUATED" or r["official_value"] != "OFFICIAL_VALUE_PENDING" for r in per_req)
        and len(envs["environments"]) == 7
        and {m["id"] for m in methods["methods"]} == {"SIMULATION", "ANALYTICAL", "INSPECTION"}
        and len(scenarios["scenarios"]) == 6
    )
    return {
        "schema": "gunnchos.net_sec_rc001.imt2030_eval_harness.v1",
        "ok": ok,
        "IMT2030_PASS": None,  # intentionally absent / null — no global pass token
        "global_imt2030_pass_forbidden": True,
        "per_requirement": per_req,
        "environments": env_report,
        "methods": [m["id"] for m in methods["methods"]],
        "scenarios": [s["id"] for s in scenarios["scenarios"]],
        "IndoorFactory_HRLLC_present": any(e["id"] == "IndoorFactory-HRLLC" for e in envs["environments"]),
        "IndoorFactory_ISAC_present": any(e["id"] == "IndoorFactory-ISAC" for e in envs["environments"]),
        "UrbanMacro_ISAC_present": any(e["id"] == "UrbanMacro-ISAC" for e in envs["environments"]),
        "claim_boundary": "Per-requirement evidence only; no global IMT2030_PASS.",
        "token_candidate": "IMT2030_EVAL_HARNESS_CURRENT_DRAFT",
    }
