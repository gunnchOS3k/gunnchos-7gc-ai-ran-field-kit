"""Independent verifier — recalculates metrics from raw JSON outputs only."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.replication.ladder import contiguous_earned
from research.r6g.replication.stats import summarize, win_rate

ROOT = Path(__file__).resolve().parents[3]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_r6g003(raw: Path) -> dict[str, Any]:
    primary = sorted(raw.glob("primary_s*.json"))
    if not primary:
        return {"ok": False, "reason": "no primary raw files"}
    deltas = []
    wins = []
    for p in primary:
        row = _load(p)
        # Recalculate delta from modality matrix — do not trust stored delta alone
        rf = row["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        all_m = row["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        delta = round(all_m - rf, 4)
        stored = row.get("rf_all_vs_rf_only_delta_m")
        if stored is not None and abs(stored - delta) > 1e-3:
            return {"ok": False, "reason": f"delta mismatch in {p.name}", "stored": stored, "recalc": delta}
        deltas.append(delta)
        wins.append(delta < 0.0)
    neg = list(raw.glob("neg_s*.json")) + list(raw.glob("neg_*.json"))
    neg_worse = 0
    for p in neg:
        row = _load(p)
        rf = row["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        all_m = row["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        if all_m - rf > 0:
            neg_worse += 1
    return {
        "ok": True,
        "n_primary": len(primary),
        "delta_summary": summarize(deltas),
        "win_rate": win_rate(wins),
        "negative_worse_count": neg_worse,
        "falsifiable": neg_worse >= 1,
        "primary_mean_delta_negative": (summarize(deltas)["mean"] or 0) < 0,
    }


def _verify_r6g005(raw: Path) -> dict[str, Any]:
    path = raw / "full_report.json"
    if not path.exists():
        return {"ok": False, "reason": "missing full_report.json"}
    r = _load(path)
    # Recalculate support: aware failure under adversarial < naive
    naive_f = r["results"]["AI_CSF"]["adversarial_csi"]["failure_rate"]
    aware_f = r["results"]["AI_CSF_UNCERTAINTY_AWARE"]["adversarial_csi"]["failure_rate"]
    id_aware_t = r["results"]["AI_CSF_UNCERTAINTY_AWARE"]["in_distribution"]["throughput_norm"]
    id_conv_t = r["results"]["CONVENTIONAL_CSI"]["in_distribution"]["throughput_norm"]
    support = aware_f < naive_f
    # Documented no-gain on IID if aware throughput <= conventional
    no_gain_id = id_aware_t <= id_conv_t
    return {
        "ok": True,
        "aware_beats_naive_adversarial_failure": support,
        "recalc_naive_failure": naive_f,
        "recalc_aware_failure": aware_f,
        "iid_no_gain_vs_conventional": no_gain_id,
        "documented_negatives": len(r.get("documented_negative_or_no_gain", [])),
        "falsifiable": len(r.get("documented_negative_or_no_gain", [])) >= 1,
    }


def _verify_r6g009(raw: Path) -> dict[str, Any]:
    path = raw / "full_report.json"
    if not path.exists():
        return {"ok": False, "reason": "missing full_report.json"}
    r = _load(path)
    g25 = r["delay_grid_ms"]["25"]
    g100 = r["delay_grid_ms"]["100"]
    pred25 = g25["PREDICTIVE_BELIEF_STATE"]["policy_regret"]
    cur25 = g25["CURRENT_STATE_ONLY"]["policy_regret"]
    pred100 = g100["PREDICTIVE_BELIEF_STATE"]["policy_regret"]
    cur100 = g100["CURRENT_STATE_ONLY"]["policy_regret"]
    moderate_win = pred25 < cur25
    long_horizon_loss = pred100 >= cur100
    return {
        "ok": True,
        "moderate_delay_improvement_recalc": moderate_win,
        "long_horizon_no_gain_recalc": long_horizon_loss,
        "pred25": pred25,
        "cur25": cur25,
        "pred100": pred100,
        "cur100": cur100,
        "falsifiable": long_horizon_loss or bool(r.get("negative_suite", {}).get("jump_no_gain")),
    }


def verify_from_raw(replication_dir: Path | None = None) -> dict[str, Any]:
    base = Path(replication_dir) if replication_dir else (ROOT / "artifacts" / "r6g" / "replication")
    raw = base / "raw"
    v003 = _verify_r6g003(raw / "R6G-003")
    v005 = _verify_r6g005(raw / "R6G-005")
    v009 = _verify_r6g009(raw / "R6G-009")

    suite_path = base / "R6G_REPLICATION_SUITE.json"
    suite = _load(suite_path) if suite_path.exists() else {}

    pass003 = bool(v003.get("ok") and v003.get("primary_mean_delta_negative") and v003.get("falsifiable"))
    pass005 = bool(v005.get("ok") and v005.get("aware_beats_naive_adversarial_failure") and v005.get("falsifiable"))
    pass009 = bool(v009.get("ok") and v009.get("moderate_delay_improvement_recalc") and v009.get("falsifiable"))
    independent_pass = pass003 and pass005 and pass009

    # Update ladder R6 flags in suite copy
    if suite.get("candidates"):
        for key, ok in (("R6G-003", pass003), ("R6G-005", pass005), ("R6G-009", pass009)):
            c = suite["candidates"][key]
            c["ladder_flags"]["R6"] = ok
            c["ladder_earned"] = contiguous_earned(c["ladder_flags"])
            if ok and c["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE":
                c["claim_state"] = "PROMISING_DIGITAL"
        suite["tokens"]["R6G_INDEPENDENT_VERIFIER_PASS"] = independent_pass
        # Digital replication pass may upgrade if R6 earned
        suite["tokens"]["R6G_DIGITAL_REPLICATION_PASS"] = all(
            set(["R3", "R4", "R5", "R6"]).issubset(set(suite["candidates"][k]["ladder_earned"]))
            for k in ("R6G-003", "R6G-005", "R6G-009")
        )

    report = {
        "schema": "gunnchos.r6g.independent_verifier.v1",
        "ok": independent_pass,
        "method": "recalculate_from_raw_json_only",
        "R6G-003": v003,
        "R6G-005": v005,
        "R6G-009": v009,
        "R6G_INDEPENDENT_VERIFIER_PASS": independent_pass,
        "IMPROVED_STATE_OF_ART": False,
        "BREAKTHROUGH_PROVEN": False,
        "note": "Verifier confirms digital arithmetic; does not confer physical SoA.",
    }
    assert_no_soa(report)
    (base / "R6G_INDEPENDENT_VERIFIER.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if suite:
        suite["independent_verifier"] = report
        (base / "R6G_REPLICATION_SUITE.json").write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    r = verify_from_raw()
    print("INDEPENDENT_VERIFIER_PASS" if r["ok"] else "INDEPENDENT_VERIFIER_FAIL")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
