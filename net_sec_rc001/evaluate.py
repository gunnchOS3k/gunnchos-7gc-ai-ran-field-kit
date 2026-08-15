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
from .terrestrial_rel16 import RM520NTerrestrialDigital
from .tokens import (
    CLAIM_BOUNDARY,
    EARNABLE_TOKENS,
    FORBIDDEN_TOKENS,
    PRODUCT_WORDING,
    SUPPORTING_TOKENS,
    assert_forbidden_remain_false,
    empty_token_table,
)
from research.r6g.evaluate import evaluate_r6g

ROOT = Path(__file__).resolve().parents[1]


def evaluate_net_sec_rc001(out_dir: Path | None = None) -> dict[str, Any]:
    modules = {
        "terrestrial_rel16": RM520NTerrestrialDigital().run(),
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
    r6g_out = (Path(out_dir) / "r6g") if out_dir is not None else (ROOT / "artifacts" / "r6g")
    r6g = evaluate_r6g(r6g_out)

    tokens = empty_token_table()
    # Honesty: Rel-16 RM520N digital sim does NOT earn 5GA.
    tokens["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] = False
    tokens["5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"] = bool(modules["terrestrial_rel16"]["ok"])
    tokens["NTN_SIMULATION_RUNTIME"] = bool(modules["ntn_sim"]["ok"])
    tokens["AI_RAN_DIGITAL_RUNTIME"] = bool(modules["ai_ran_safe"]["ok"])
    tokens["SERVICE_CONTINUITY_POLICY"] = bool(modules["service_continuity"]["ok"])
    tokens["APP_QOS_QOE_DIGITAL"] = bool(modules["app_qos_qoe"]["ok"])
    tokens["HOSTILE_NETWORK_DIGITAL"] = bool(modules["hostile_network"]["ok"])
    tokens["IMT2030_EVAL_HARNESS_CURRENT_DRAFT"] = bool(modules["imt2030_eval"]["ok"])
    tokens["REL20_REL21_MIGRATION_TRACKER"] = bool(modules["migration_6g"]["ok"])
    tokens["IMT2030_MAPPING_COMPLETE_CURRENT_PUBLIC_DRAFT"] = bool(
        modules["imt2030_eval"]["ok"] and modules["migration_6g"]["ok"]
    )
    # R6G extension tokens (honest digital-only)
    tokens["R6G_REGISTRY_COMPLETE"] = bool(r6g["tokens"]["R6G_REGISTRY_COMPLETE"])
    tokens["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"] = bool(r6g["tokens"]["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"])
    tokens["AI_PHY_UNCERTAINTY_AWARE_DIGITAL"] = bool(r6g["tokens"]["AI_PHY_UNCERTAINTY_AWARE_DIGITAL"])
    tokens["PREDICTIVE_RADIO_DT_DIGITAL"] = bool(r6g["tokens"]["PREDICTIVE_RADIO_DT_DIGITAL"])
    tokens["HYBRID_SPECTRUM_FABRIC_DIGITAL"] = bool(r6g["tokens"]["HYBRID_SPECTRUM_FABRIC_DIGITAL"])
    tokens["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] = bool(r6g["tokens"]["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"])
    tokens["IMPROVED_STATE_OF_ART"] = False
    for k in FORBIDDEN_TOKENS:
        tokens[k] = False
    assert_forbidden_remain_false(tokens)
    assert tokens["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] is False
    assert tokens["IMPROVED_STATE_OF_ART"] is False
    assert modules["terrestrial_rel16"]["five_ga_capable"] is False
    assert modules["terrestrial_rel16"]["release"] == "Rel-16"

    digital_ok = all(modules[k]["ok"] for k in modules) and bool(r6g["ok"])
    open_list = [
        "5GA_TERRESTRIAL_DIGITAL_RUNTIME remains false — Rel-16 RM520N digital ≠ 5G-Advanced; need distinct Rel-18+/5GA software surface to earn",
        "CARRIER attach / operator acceptance EXTERNAL_PENDING",
        "SM-DP+ / real eSIM profile download EXTERNAL_PENDING",
        "Official ITU TPR numeric values OFFICIAL_VALUE_PENDING (Doc 5/116 TIES / SG5 Dec 2026)",
        "Official per-requirement evaluation-method assignment OFFICIAL_ASSIGNMENT_PENDING",
        "Test-environment parameter tables OFFICIAL_PARAMS_PENDING",
        "Large ns-3/Sionna/DeepMIMO sweeps DEFERRED (resource rule)",
        "Large twin renders / multi-hour RF sims / extra QEMU DEFERRED",
        "REAL_NTN_MODEM_VALIDATED remains false",
        "GATE_8_PASS / STANDARDIZED_6G remain false",
        "IMPROVED_STATE_OF_ART remains false — physical SoA not claimed",
        "R6G atlas DOI/PDF pins PENDING for many baselines",
        "DIGITAL_REPRODUCTION_MATCHED to published physical values generally false (structural)",
        "R5 independent digital improvement verification not claimed",
        "R6G-004/006/007/008/010/011 REGISTERED_NOT_ACTIVE",
        "Field 7GC community outcomes not fabricated — field measurement OPEN",
        "RF/Wi-Fi hostile physical E5/E8 EXTERNAL_PENDING",
    ]
    open_list.extend(r6g.get("OPEN", []))

    deferred = [
        "ns-3 / Sionna / DeepMIMO campaign sweeps",
        "multi-hour RF / NTN / THz physical campaigns",
        "large digital-twin renders",
        "extra QEMU guests (Product-Use likely active)",
        "large model downloads for AI-RAN",
        "long soak / carrier lab attaches",
        "distinct Rel-18+/5GA terrestrial digital runtime (not RM520N Rel-16)",
    ]
    deferred.extend(r6g.get("deferred_heavy_work", []))

    report = {
        "schema": "gunnchos.net_sec_rc001.aggregate.v1",
        "packet": "NET-SEC-6G-RC-001",
        "remediation": "PR78_R6G_FALSIFIABLE_DEMOTE_TAUTOLOGIES_AND_NAKED_HEADLINES",
        "r6g_extension": "R6G_BREAKTHROUGH_PROGRAM_ACTIVE_SUBPACKETS",
        "ok": digital_ok,
        "exit_state": "DIGITALLY_VALIDATED" if digital_ok else "INCOMPLETE_DIGITAL",
        "product_wording": PRODUCT_WORDING,
        "claim_boundary": CLAIM_BOUNDARY,
        "tokens": tokens,
        "earnable_tokens": list(EARNABLE_TOKENS),
        "supporting_tokens": list(SUPPORTING_TOKENS),
        "forbidden_tokens": list(FORBIDDEN_TOKENS),
        "IMPROVED_STATE_OF_ART": False,
        "modules": {k: {"ok": v["ok"], "schema": v.get("schema")} for k, v in modules.items()},
        "module_details": modules,
        "r6g": {
            "ok": r6g["ok"],
            "breakthroughs_registered": r6g["breakthroughs_registered"],
            "active_packet_status": r6g["active_packet_status"],
            "registered_not_active": r6g["registered_not_active"],
            "tokens": r6g["tokens"],
            "digital_improvements_observed": r6g["digital_improvements_observed"],
            "independent_improvements_verified": r6g["independent_improvements_verified"],
            "physical_pending": r6g["physical_pending"],
            "product_candidates": r6g["product_candidates"],
            "negative_or_no_gain_notes": r6g["negative_or_no_gain_notes"],
            "documented_negative_experiments": r6g.get("documented_negative_experiments", {}),
            "falsifiability": r6g.get("falsifiability", {}),
            "naked_numeric_headline_count": r6g.get("naked_numeric_headline_count", None),
        },
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
            json.dumps(
                {
                    "tokens": tokens,
                    "product_wording": PRODUCT_WORDING,
                    "supporting_tokens": list(SUPPORTING_TOKENS),
                    "note": (
                        "5GA_TERRESTRIAL_DIGITAL_RUNTIME=false; Rel-16 surface uses "
                        "5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME. R6G multimodal/AI-PHY/predictive "
                        "tokens re-earned only via falsifiable digital experiments with "
                        "documented negative/no-gain cases. IMPROVED_STATE_OF_ART=false."
                    ),
                    "r6g_falsifiability": r6g.get("falsifiability"),
                    "naked_numeric_headline_count": r6g.get("naked_numeric_headline_count"),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (out_dir / "AUTHOR_SELF_CHECK.json").write_text(
            json.dumps(
                {
                    "schema": "gunnchos.net_sec_rc001.author_self_check.v1",
                    "ok": digital_ok,
                    "remediation": "PR78_R6G_FALSIFIABLE_DEMOTE_TAUTOLOGIES_AND_NAKED_HEADLINES",
                    "challenges": {
                        "5ga_false": tokens["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] is False,
                        "rel16_true": tokens["5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"] is True,
                        "r6g_registry": tokens["R6G_REGISTRY_COMPLETE"] is True,
                        "improved_soa_false": tokens["IMPROVED_STATE_OF_ART"] is False,
                        "forbidden_false": all(tokens[k] is False for k in FORBIDDEN_TOKENS),
                        "breakthroughs_ge_20": r6g["breakthroughs_registered"] >= 20,
                        "no_matched_physical": r6g["baselines_digitally_matched_to_published_physical"] is False,
                        "naked_headlines_zero": r6g.get("naked_numeric_headline_count", -1) == 0,
                        "r6g003_falsifiable": bool(r6g.get("falsifiability", {}).get("R6G-003")),
                        "r6g005_falsifiable": bool(r6g.get("falsifiability", {}).get("R6G-005")),
                        "r6g009_falsifiable": bool(r6g.get("falsifiability", {}).get("R6G-009")),
                        "documented_negatives": all(
                            len(r6g.get("documented_negative_experiments", {}).get(k, [])) >= 1
                            for k in ("R6G-003", "R6G-005", "R6G-009")
                        ),
                        "hybrid_kept": tokens["HYBRID_SPECTRUM_FABRIC_DIGITAL"] is True,
                        "semantic_kept": tokens["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] is True,
                        "product_wording_rel16": "Rel-16" in PRODUCT_WORDING,
                    },
                    "token_status": {
                        "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT": tokens["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"],
                        "AI_PHY_UNCERTAINTY_AWARE_DIGITAL": tokens["AI_PHY_UNCERTAINTY_AWARE_DIGITAL"],
                        "PREDICTIVE_RADIO_DT_DIGITAL": tokens["PREDICTIVE_RADIO_DT_DIGITAL"],
                        "HYBRID_SPECTRUM_FABRIC_DIGITAL": tokens["HYBRID_SPECTRUM_FABRIC_DIGITAL"],
                        "SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL": tokens["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"],
                        "IMPROVED_STATE_OF_ART": False,
                        "6G_BREAKTHROUGH_PASS": None,
                    },
                    "note": (
                        "Author self-check after R6G tautology/naked-headline remediation on PR #78. "
                        "IMPROVED_STATE_OF_ART=false. Cursor does not merge."
                    ),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return report


def main() -> int:
    report = evaluate_net_sec_rc001(ROOT / "artifacts" / "net_sec_rc001")
    print("NET_SEC_6G_RC001_PASS" if report["ok"] else "NET_SEC_6G_RC001_FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
