"""NET-SEC-6G-RC-001 unit tests — digital only, honest claims."""
from __future__ import annotations

import json
from pathlib import Path

from net_sec_rc001 import evaluate_net_sec_rc001
from net_sec_rc001.tokens import (
    EARNABLE_TOKENS,
    FORBIDDEN_TOKENS,
    PRODUCT_WORDING,
    SUPPORTING_TOKENS,
)
from standards.harnesses.imt2030_rel20_rel21_tracker import evaluate as evaluate_tracker

ROOT = Path(__file__).resolve().parents[1]

PRESERVED_TRUE = (
    "NTN_SIMULATION_RUNTIME",
    "AI_RAN_DIGITAL_RUNTIME",
    "SERVICE_CONTINUITY_POLICY",
    "APP_QOS_QOE_DIGITAL",
    "HOSTILE_NETWORK_DIGITAL",
    "IMT2030_MAPPING_COMPLETE_CURRENT_PUBLIC_DRAFT",
    "IMT2030_EVAL_HARNESS_CURRENT_DRAFT",
    "REL20_REL21_MIGRATION_TRACKER",
)


def test_product_wording_does_not_claim_rm520n_is_5ga_or_ntn():
    assert "Rel-16" in PRODUCT_WORDING
    assert "not 5G-Advanced hardware" in PRODUCT_WORDING
    assert "not NTN" in PRODUCT_WORDING
    assert "migration to standardized 6G" in PRODUCT_WORDING
    # Must not imply the modem SKU itself is 5GA/NTN-capable without qualification
    assert "RM520N-GL digital baseline is Rel-16" in PRODUCT_WORDING


def test_machine_readable_standards_json_present():
    for name in (
        "framework.json",
        "technical_performance_requirements.json",
        "evaluation_methods.json",
        "test_environments.json",
        "usage_scenarios.json",
    ):
        path = ROOT / "standards" / "imt2030" / name
        assert path.is_file(), name
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["claim_boundary"]["STANDARDIZED_6G"] is False
    rel = json.loads((ROOT / "standards" / "3gpp" / "release_tracker.json").read_text(encoding="utf-8"))
    assert rel["release_21"]["freeze_claimed"] is False


def test_tpr_no_invented_official_numbers():
    tpr = json.loads(
        (ROOT / "standards" / "imt2030" / "technical_performance_requirements.json").read_text(encoding="utf-8")
    )
    assert tpr["requirement_count"] == 20
    assert len(tpr["requirements"]) == 20
    for req in tpr["requirements"]:
        assert req["official_value"] == "OFFICIAL_VALUE_PENDING"


def test_environments_include_new_isac_hrllc():
    envs = json.loads(
        (ROOT / "standards" / "imt2030" / "test_environments.json").read_text(encoding="utf-8")
    )
    ids = {e["id"] for e in envs["environments"]}
    assert {"IndoorFactory-HRLLC", "IndoorFactory-ISAC", "UrbanMacro-ISAC"} <= ids


def test_scenarios_ic_hrllc_mc_uc_aiac_isac():
    scenarios = json.loads(
        (ROOT / "standards" / "imt2030" / "usage_scenarios.json").read_text(encoding="utf-8")
    )
    ids = {s["id"] for s in scenarios["scenarios"]}
    assert ids == {"IC", "HRLLC", "MC", "UC", "AIAC", "ISAC"}


def test_aggregate_honest_tokens(tmp_path: Path):
    report = evaluate_net_sec_rc001(tmp_path)
    assert report["ok"] is True
    tokens = report["tokens"]
    assert tokens["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] is False
    assert tokens["5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"] is True
    for key in PRESERVED_TRUE:
        assert tokens[key] is True, key
    for key in FORBIDDEN_TOKENS:
        assert tokens[key] is False, key
    assert report["module_details"]["terrestrial_rel16"]["ntn_capable"] is False
    assert report["module_details"]["terrestrial_rel16"]["five_ga_capable"] is False
    assert report["module_details"]["terrestrial_rel16"]["release"] == "Rel-16"
    assert report["module_details"]["terrestrial_rel16"]["CARRIER"] == "EXTERNAL_PENDING"
    assert report["module_details"]["esim_interfaces"]["sm_dp_plus"] == "EXTERNAL_PENDING"
    assert report["module_details"]["imt2030_eval"]["IMT2030_PASS"] is None
    # Hostile must have hit a local runtime case
    hostile = report["module_details"]["hostile_network"]
    assert hostile["uncontrolled_external_attack"] is False
    case_ids = {c["case_id"] for c in hostile["cases"]}
    assert "HN-TLS-SOCKET-001" in case_ids
    assert "HN-COUPLE-REL16-CONTINUITY-001" in case_ids
    assert (tmp_path / "NET_SEC_6G_RC001_RESULT.json").is_file()


def test_rm520n_not_ntn_or_5ga_or_6g():
    from net_sec_rc001.terrestrial_rel16 import RM520NTerrestrialDigital

    modem = RM520NTerrestrialDigital()
    assert modem.ntn_capable is False
    assert modem.five_ga_capable is False
    assert modem.six_g_capable is False
    report = modem.run()
    assert report["ok"] is True
    assert report["token_candidate"] == "5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"
    assert report["does_not_earn"] == "5GA_TERRESTRIAL_DIGITAL_RUNTIME"


def test_games_qos_class_realtime():
    from net_sec_rc001.app_qos_qoe import run_app_qos_qoe

    report = run_app_qos_qoe()
    assert report["ok"] is True
    games = [m for m in report["matrix"] if m["app"] == "games"]
    assert games
    assert all(m["qos_class"] == "realtime" for m in games)


def test_ai_ran_refuses_unsafe_carrier_control():
    from net_sec_rc001.ai_ran_safe import FORBIDDEN_ACTIONS, run_ai_ran_safe

    report = run_ai_ran_safe()
    assert report["ok"] is True
    assert report["recommendation"]["carrier_control"] is False
    assert "force_carrier_attach" in FORBIDDEN_ACTIONS


def test_equitable_7gc_no_fabricated_community_outcomes():
    from net_sec_rc001.equitable_7gc import run_equitable_7gc

    report = run_equitable_7gc()
    assert report["ok"] is True
    for s in report["scenarios"]:
        assert s["community_outcome_fabricated"] is False
        assert s["coverage_fraction_measured"] is None


def test_tracker_still_passes_with_refreshed_snapshots(tmp_path: Path):
    report = evaluate_tracker(tmp_path)
    assert report["ok"] is True
    assert report["STANDARDIZED_6G"] is False
    assert report["GATE_8_PASS"] is False


def test_author_self_check_challenges(tmp_path: Path):
    report = evaluate_net_sec_rc001(tmp_path)
    challenges = {
        "rel21_freeze_claimed_false": json.loads(
            (ROOT / "standards" / "3gpp" / "release_tracker.json").read_text(encoding="utf-8")
        )["release_21"]["freeze_claimed"]
        is False,
        "no_numeric_official_values": all(
            r["official_value"] == "OFFICIAL_VALUE_PENDING"
            for r in json.loads(
                (ROOT / "standards" / "imt2030" / "technical_performance_requirements.json").read_text(
                    encoding="utf-8"
                )
            )["requirements"]
        ),
        "5ga_false_rel16_true": report["tokens"]["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] is False
        and report["tokens"]["5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"] is True,
        "preserved_true": all(report["tokens"][k] is True for k in PRESERVED_TRUE),
        "forbidden_false": all(report["tokens"][k] is False for k in FORBIDDEN_TOKENS),
        "rm520n_not_ntn_or_5ga": report["module_details"]["terrestrial_rel16"]["ntn_capable"] is False
        and report["module_details"]["terrestrial_rel16"]["five_ga_capable"] is False,
        "no_global_imt2030_pass": report["module_details"]["imt2030_eval"]["IMT2030_PASS"] is None,
        "hostile_local_runtime": report["module_details"]["hostile_network"]["ok"] is True
        and report["module_details"]["hostile_network"]["uncontrolled_external_attack"] is False
        and any(
            c["case_id"] == "HN-TLS-SOCKET-001" and c["passed"]
            for c in report["module_details"]["hostile_network"]["cases"]
        ),
        "earnable_includes_5ga_key": "5GA_TERRESTRIAL_DIGITAL_RUNTIME" in EARNABLE_TOKENS,
        "supporting_includes_rel16": "5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME" in SUPPORTING_TOKENS,
    }
    assert all(challenges.values()), challenges
    (tmp_path / "AUTHOR_SELF_CHECK.json").write_text(
        json.dumps({"ok": True, "challenges": challenges}, indent=2) + "\n", encoding="utf-8"
    )
