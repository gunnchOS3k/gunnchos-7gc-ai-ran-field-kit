"""Aggregate NET-SEC-6G-RC-001 evaluation + token earning."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ai_ran_safe import run_ai_ran_safe
from .app_qos_qoe import run_app_qos_qoe
from .equitable_7gc import run_equitable_7gc
from .esim_interfaces import run_esim_digital
from .hostile_network import run_hostile_network_digital
from .imt2030_eval import run_imt2030_eval_harness
from .migration_6g import run_migration_abstraction
from .ntn_sim import run_ntn_simulation
from .service_continuity import run_service_continuity
from .terrestrial_5ga import RM520NTerrestrialDigital
from .tokens import (
    CLAIM_BOUNDARY,
    EARNABLE_TOKENS,
    FORBIDDEN_TOKENS,
    PRODUCT_WORDING,
    assert_forbidden_remain_false,
    empty_token_table,
)

ROOT = Path(__file__).resolve().parents[1]


def evaluate_net_sec_rc001(out_dir: Path | None = None) -> dict[str, Any]:
    modules = {
        "terrestrial_5ga": RM520NTerrestrialDigital().run(),
        "esim_interfaces": run_esim_digital(),
        "ntn_sim": run_ntn_simulation(),
        "ai_ran_safe": run_ai_ran_safe(),
        "service_continuity": run_service_continuity(),
        "app_qos_qoe": run_app_qos_qoe(),
        "hostile_network": run_hostile_network_digital(),
        "migration_6g": run_migration_abstraction(),
        "equitable_7gc": run_equitable_7gc(),
        "imt2030_eval": run_imt2030_eval_harness(),
    }

    tokens = empty_token_table()
    tokens["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] = bool(modules["terrestrial_5ga"]["ok"])
    tokens["NTN_SIMULATION_RUNTIME"] = bool(modules["ntn_sim"]["ok"])
    tokens["AI_RAN_DIGITAL_RUNTIME"] = bool(modules["ai_ran_safe"]["ok"])
    tokens["SERVICE_CONTINUITY_POLICY"] = bool(modules["service_continuity"]["ok"])
    tokens["APP_QOS_QOE_DIGITAL"] = bool(modules["app_qos_qoe"]["ok"])
    tokens["HOSTILE_NETWORK_DIGITAL"] = bool(modules["hostile_network"]["ok"])
    tokens["IMT2030_EVAL_HARNESS_CURRENT_DRAFT"] = bool(modules["imt2030_eval"]["ok"])
    tokens["REL20_REL21_MIGRATION_TRACKER"] = bool(modules["migration_6g"]["ok"])
    # Mapping complete for current public draft = scenarios+envs+tpr slots present with honest pending values
    tokens["IMT2030_MAPPING_COMPLETE_CURRENT_PUBLIC_DRAFT"] = bool(
        modules["imt2030_eval"]["ok"] and modules["migration_6g"]["ok"]
    )
    # Forbidden remain false
    for k in FORBIDDEN_TOKENS:
        tokens[k] = False
    assert_forbidden_remain_false(tokens)

    digital_ok = all(modules[k]["ok"] for k in modules)
    open_list = []
    if modules["terrestrial_5ga"]["CARRIER"] == "EXTERNAL_PENDING":
        open_list.append("CARRIER attach / operator acceptance EXTERNAL_PENDING")
    if modules["esim_interfaces"]["sm_dp_plus"] == "EXTERNAL_PENDING":
        open_list.append("SM-DP+ / real eSIM profile download EXTERNAL_PENDING")
    open_list.extend(
        [
            "Official ITU TPR numeric values OFFICIAL_VALUE_PENDING (Doc 5/116 TIES / SG5 Dec 2026)",
            "Official per-requirement evaluation-method assignment OFFICIAL_ASSIGNMENT_PENDING",
            "Test-environment parameter tables OFFICIAL_PARAMS_PENDING",
            "Large ns-3/Sionna/DeepMIMO sweeps DEFERRED (resource rule)",
            "Large twin renders / multi-hour RF sims / extra QEMU DEFERRED",
            "REAL_NTN_MODEM_VALIDATED remains false",
            "GATE_8_PASS / STANDARDIZED_6G remain false",
            "Field 7GC community outcomes not fabricated — field measurement OPEN",
            "RF/Wi-Fi hostile physical E5/E8 EXTERNAL_PENDING",
        ]
    )

    deferred = [
        "ns-3 / Sionna / DeepMIMO campaign sweeps",
        "multi-hour RF / NTN physical campaigns",
        "large digital-twin renders",
        "extra QEMU guests (Product-Use likely active)",
        "large model downloads for AI-RAN",
        "long soak / carrier lab attaches",
    ]

    report = {
        "schema": "gunnchos.net_sec_rc001.aggregate.v1",
        "packet": "NET-SEC-6G-RC-001",
        "ok": digital_ok,
        "exit_state": "DIGITALLY_VALIDATED" if digital_ok else "INCOMPLETE_DIGITAL",
        "product_wording": PRODUCT_WORDING,
        "claim_boundary": CLAIM_BOUNDARY,
        "tokens": tokens,
        "earnable_tokens": list(EARNABLE_TOKENS),
        "forbidden_tokens": list(FORBIDDEN_TOKENS),
        "modules": {k: {"ok": v["ok"], "schema": v.get("schema")} for k, v in modules.items()},
        "module_details": modules,
        "owners": {
            "primary": "gunnchos-7gc-ai-ran-field-kit",
            "supporting": [
                "gunnchos-device-os (5G-A/eSIM surfaces; Product-Use QEMU active — not disturbed)",
                "ntn-resilience-sim",
                "spectrumx-ai-ran-gary",
                "gunnchos-6g-security-trust-privacy-lab",
                "7gc-digital-twin",
                "edge-io-measurement-node",
            ],
        },
        "standards_versions": {
            "ITU-R_M.2160": "APPROVED",
            "IMT-2030.TECH_PERF_REQ": "WP5D draft Feb 2026 / Doc 5/116 → SG5 Dec 2026",
            "IMT-2030.EVAL": "WP5D draft Jun 2026 / Doc 5/119 → SG5 Dec 2026",
            "3GPP_Rel-20": "5G-Advanced + 6G studies (in progress)",
            "3GPP_Rel-21": "TRACKER_ONLY timeline published TSGs#112 Jun 2026",
            "GSMA_SGP.22": "v2.7 (2026-04-24)",
            "GSMA_Open_Gateway_CAMARA": "public API catalog; REAL_OPERATOR EXTERNAL_PENDING",
        },
        "OPEN": open_list,
        "deferred_heavy_work": deferred,
        "mock": False,
    }

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "NET_SEC_6G_RC001_RESULT.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (out_dir / "TOKEN_TABLE.json").write_text(
            json.dumps({"tokens": tokens, "product_wording": PRODUCT_WORDING}, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> int:
    report = evaluate_net_sec_rc001(ROOT / "artifacts" / "net_sec_rc001")
    print("NET_SEC_6G_RC001_PASS" if report["ok"] else "NET_SEC_6G_RC001_FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
