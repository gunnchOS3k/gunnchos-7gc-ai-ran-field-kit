"""NET-SEC-6G-RC-001 unit tests — digital only, honest claims."""
from __future__ import annotations

import json
from pathlib import Path

from net_sec_rc001 import evaluate_net_sec_rc001
from net_sec_rc001.tokens import EARNABLE_TOKENS, FORBIDDEN_TOKENS, PRODUCT_WORDING
from standards.harnesses.imt2030_rel20_rel21_tracker import evaluate as evaluate_tracker

ROOT = Path(__file__).resolve().parents[1]


def test_product_wording_exact():
    assert PRODUCT_WORDING == (
        "5G-Advanced and NTN-capable, IMT-2030-aligned, software-defined, "
        "and engineered for migration to standardized 6G."
    )


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
        assert req["evidence_state"] in {
            "REQUIREMENT_EVALUATED",
            "NOT_YET_EVALUATABLE",
            "STANDARD_PENDING",
        }


def test_environments_include_new_isac_hrllc():
    envs = json.loads(
        (ROOT / "standards" / "imt2030" / "test_environments.json").read_text(encoding="utf-8")
    )
    ids = {e["id"] for e in envs["environments"]}
    assert "IndoorFactory-HRLLC" in ids
    assert "IndoorFactory-ISAC" in ids
    assert "UrbanMacro-ISAC" in ids
    assert all(e["params_status"] == "OFFICIAL_PARAMS_PENDING" for e in envs["environments"])


def test_scenarios_ic_hrllc_mc_uc_aiac_isac():
    scenarios = json.loads(
        (ROOT / "standards" / "imt2030" / "usage_scenarios.json").read_text(encoding="utf-8")
    )
    ids = {s["id"] for s in scenarios["scenarios"]}
    assert ids == {"IC", "HRLLC", "MC", "UC", "AIAC", "ISAC"}


def test_aggregate_earns_digital_tokens_only(tmp_path: Path):
    report = evaluate_net_sec_rc001(tmp_path)
    assert report["ok"] is True
    for key in EARNABLE_TOKENS:
        assert report["tokens"][key] is True, key
    for key in FORBIDDEN_TOKENS:
        assert report["tokens"][key] is False, key
    assert report["module_details"]["terrestrial_5ga"]["ntn_capable"] is False
    assert report["module_details"]["terrestrial_5ga"]["CARRIER"] == "EXTERNAL_PENDING"
    assert report["module_details"]["esim_interfaces"]["sm_dp_plus"] == "EXTERNAL_PENDING"
    assert report["module_details"]["ntn_sim"]["RM520N_GL_NTN"] is False
    assert report["module_details"]["imt2030_eval"]["IMT2030_PASS"] is None
    assert report["module_details"]["imt2030_eval"]["global_imt2030_pass_forbidden"] is True
    assert (tmp_path / "NET_SEC_6G_RC001_RESULT.json").is_file()


def test_rm520n_not_ntn_or_6g():
    from net_sec_rc001.terrestrial_5ga import RM520NTerrestrialDigital

    modem = RM520NTerrestrialDigital()
    assert modem.ntn_capable is False
    assert modem.six_g_capable is False
    report = modem.run()
    assert report["ok"] is True
    assert report["ntn_capable"] is False
    assert report["six_g_capable"] is False


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
    assert report["rel21"]["freeze_claimed"] is False


def test_author_self_check_challenges(tmp_path: Path):
    """Independent-verifier style challenges (author self-check)."""
    report = evaluate_net_sec_rc001(tmp_path)
    challenges = {}

    # Challenge 1: mutate Rel-21 freeze_claimed true should be detectable in tracker JSON source
    rel_path = ROOT / "standards" / "3gpp" / "release_tracker.json"
    rel = json.loads(rel_path.read_text(encoding="utf-8"))
    challenges["rel21_freeze_claimed_false"] = rel["release_21"]["freeze_claimed"] is False

    # Challenge 2: inventing an official TPR number must not be present
    tpr = json.loads(
        (ROOT / "standards" / "imt2030" / "technical_performance_requirements.json").read_text(encoding="utf-8")
    )
    challenges["no_numeric_official_values"] = all(
        r["official_value"] == "OFFICIAL_VALUE_PENDING" for r in tpr["requirements"]
    )

    # Challenge 3: forbidden tokens false even when earnable true
    challenges["forbidden_false_while_earnable_true"] = all(
        report["tokens"][k] is False for k in FORBIDDEN_TOKENS
    ) and all(report["tokens"][k] is True for k in EARNABLE_TOKENS)

    # Challenge 4: RM520N NTN not claimed
    challenges["rm520n_not_ntn"] = report["module_details"]["terrestrial_5ga"]["ntn_capable"] is False

    # Challenge 5: no global IMT2030_PASS
    challenges["no_global_imt2030_pass"] = report["module_details"]["imt2030_eval"]["IMT2030_PASS"] is None

    # Challenge 6: hostile suite local-only
    challenges["hostile_local_only"] = (
        report["module_details"]["hostile_network"]["uncontrolled_external_attack"] is False
    )

    assert all(challenges.values()), challenges
    (tmp_path / "AUTHOR_SELF_CHECK.json").write_text(
        json.dumps({"ok": True, "challenges": challenges}, indent=2) + "\n", encoding="utf-8"
    )
