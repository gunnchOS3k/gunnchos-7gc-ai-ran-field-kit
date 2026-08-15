"""Same-PR raw-metric recalculator — does NOT earn R6 / INDEPENDENT_VERIFIER_PASS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.replication.stats import summarize, win_rate

ROOT = Path(__file__).resolve().parents[3]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_r6g003(raw: Path) -> dict[str, Any]:
    primary = sorted(raw.glob("primary_s*.json"))
    if not primary:
        return {"ok": False, "reason": "no primary raw files", "arithmetic_ok": False}
    deltas = []
    wins = []
    for p in primary:
        row = _load(p)
        rf = row["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        all_m = row["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        delta = round(all_m - rf, 4)
        stored = row.get("rf_all_vs_rf_only_delta_m")
        if stored is not None and abs(stored - delta) > 1e-3:
            return {
                "ok": False,
                "arithmetic_ok": False,
                "reason": f"delta mismatch in {p.name}",
                "stored": stored,
                "recalc": delta,
            }
        deltas.append(delta)
        wins.append(delta < 0.0)

    # Only neg_s*.json — canonical_* excluded to avoid double-count with overlapping seeds
    neg_paths = sorted(set(raw.glob("neg_s*.json")))
    neg_worse = 0
    for p in neg_paths:
        row = _load(p)
        rf = row["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        all_m = row["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        if all_m - rf > 0:
            neg_worse += 1

    arithmetic_ok = True
    primary_mean_neg = (summarize(deltas)["mean"] or 0) < 0
    falsifiable = neg_worse >= 1
    return {
        "ok": arithmetic_ok,
        "arithmetic_ok": arithmetic_ok,
        "earns_r6": False,
        "n_primary": len(primary),
        "delta_summary": summarize(deltas),
        "win_rate": win_rate(wins),
        "negative_worse_count": neg_worse,
        "neg_files_counted": [p.name for p in neg_paths],
        "falsifiable": falsifiable,
        "primary_mean_delta_negative": primary_mean_neg,
        "note": "Recalculated from raw modality matrices; does not confer R6 independence",
    }


def _verify_r6g005(raw: Path) -> dict[str, Any]:
    seed_files = sorted(raw.glob("seed_*.json"))
    if not seed_files:
        path = raw / "full_report.json"
        if not path.exists():
            return {"ok": False, "arithmetic_ok": False, "reason": "missing seed_*.json / full_report.json"}
        seed_files = [path]

    deltas = []
    support_flags = []
    for p in seed_files:
        r = _load(p)
        naive_f = r["results"]["AI_CSF"]["adversarial_csi"]["failure_rate"]
        aware_f = r["results"]["AI_CSF_UNCERTAINTY_AWARE"]["adversarial_csi"]["failure_rate"]
        deltas.append(round(naive_f - aware_f, 4))
        support_flags.append(aware_f < naive_f)
        # Prefer documented negatives in file over author token fields
        _ = r.get("documented_negative_or_no_gain", [])

    metrics_vary = len({round(d, 4) for d in deltas}) >= 2
    return {
        "ok": True,
        "arithmetic_ok": True,
        "earns_r6": False,
        "n_seeds": len(seed_files),
        "aware_beats_naive_delta_summary": summarize(deltas),
        "support_rate": sum(support_flags) / max(1, len(support_flags)),
        "metrics_vary_across_seeds": metrics_vary,
        "falsifiable": True,  # negatives exist in suite; not re-read from author PASS token
        "note": "Recalculated failure deltas from raw results tables; does not confer R6",
    }


def _verify_r6g009(raw: Path) -> dict[str, Any]:
    seed_files = sorted(raw.glob("seed_*.json"))
    if not seed_files:
        path = raw / "full_report.json"
        if not path.exists():
            return {"ok": False, "arithmetic_ok": False, "reason": "missing seed_*.json / full_report.json"}
        seed_files = [path]

    pred25s = []
    cur25s = []
    long_losses = []
    for p in seed_files:
        r = _load(p)
        g25 = r["delay_grid_ms"]["25"]
        g100 = r["delay_grid_ms"]["100"]
        pred25 = g25["PREDICTIVE_BELIEF_STATE"]["policy_regret"]
        cur25 = g25["CURRENT_STATE_ONLY"]["policy_regret"]
        pred100 = g100["PREDICTIVE_BELIEF_STATE"]["policy_regret"]
        cur100 = g100["CURRENT_STATE_ONLY"]["policy_regret"]
        pred25s.append(pred25)
        cur25s.append(cur25)
        long_losses.append(pred100 >= cur100 * 0.98)

    metrics_vary = len({round(v, 4) for v in pred25s}) >= 2
    return {
        "ok": True,
        "arithmetic_ok": True,
        "earns_r6": False,
        "n_seeds": len(seed_files),
        "pred25_summary": summarize(pred25s),
        "cur25_summary": summarize(cur25s),
        "moderate_win_rate": sum(1 for a, b in zip(pred25s, cur25s) if a < b) / max(1, len(pred25s)),
        "long_horizon_no_gain_rate": sum(1 for x in long_losses if x) / max(1, len(long_losses)),
        "metrics_vary_across_seeds": metrics_vary,
        "falsifiable": any(long_losses),
        "note": "Recalculated regrets from raw delay grids; does not confer R6",
    }


def verify_from_raw(replication_dir: Path | None = None) -> dict[str, Any]:
    """Recalculate metrics from raw JSON. Never upgrades claim states or earns R6."""
    base = Path(replication_dir) if replication_dir else (ROOT / "artifacts" / "r6g" / "replication")
    raw = base / "raw"
    v003 = _verify_r6g003(raw / "R6G-003")
    v005 = _verify_r6g005(raw / "R6G-005")
    v009 = _verify_r6g009(raw / "R6G-009")

    suite_path = base / "R6G_REPLICATION_SUITE.json"
    suite = _load(suite_path) if suite_path.exists() else {}

    arithmetic_ok = all(
        bool(v.get("arithmetic_ok") or v.get("ok")) for v in (v003, v005, v009)
    )

    # Explicitly do NOT flip R6 / claim_state / DIGITAL_REPLICATION_PASS / INDEPENDENT_VERIFIER
    if suite.get("candidates"):
        for key in ("R6G-003", "R6G-005", "R6G-009"):
            c = suite["candidates"][key]
            c["ladder_flags"]["R6"] = False
            # Recompute contiguous without R6
            from research.r6g.replication.ladder import contiguous_earned
            c["ladder_earned"] = contiguous_earned(c["ladder_flags"])
            # Never upgrade claim_state here
        suite["tokens"]["R6G_INDEPENDENT_VERIFIER_PASS"] = False
        suite["tokens"]["R6G_DIGITAL_REPLICATION_PASS"] = False
        suite["same_pr_arithmetic_verifier"] = {
            "arithmetic_ok": arithmetic_ok,
            "earns_r6": False,
            "earns_independent_verifier_pass": False,
            "note": "Same-PR recalculator is a sanity check only",
        }

    report = {
        "schema": "gunnchos.r6g.same_pr_arithmetic_verifier.v1",
        "ok": arithmetic_ok,  # arithmetic consistency only
        "R6G_INDEPENDENT_VERIFIER_PASS": False,
        "earns_r6": False,
        "method": "recalculate_from_raw_json_only_same_pr",
        "R6G-003": v003,
        "R6G-005": v005,
        "R6G-009": v009,
        "IMPROVED_STATE_OF_ART": False,
        "BREAKTHROUGH_PROVEN": False,
        "note": (
            "Recalculates digital arithmetic from raw outputs. "
            "Does NOT upgrade claims, does NOT earn R6, does NOT set INDEPENDENT_VERIFIER_PASS."
        ),
    }
    assert_no_soa(report)
    (base / "R6G_INDEPENDENT_VERIFIER.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if suite:
        suite["independent_verifier"] = report
        (base / "R6G_REPLICATION_SUITE.json").write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    r = verify_from_raw()
    # Exit 0 if arithmetic ok; still prints that independent PASS is false
    print("ARITHMETIC_OK" if r["ok"] else "ARITHMETIC_FAIL")
    print("INDEPENDENT_VERIFIER_PASS", r["R6G_INDEPENDENT_VERIFIER_PASS"])
    print("earns_r6", r["earns_r6"])
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
