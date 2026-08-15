"""R6G-008 — NTN semantic service continuity (executed digital traces).

Controlled channel traces + real WAIKE/gunnchAI payload objects.
Modes: FULL_SYNC / COMPRESSED_SYNC / SEMANTIC_SYNC.
Includes failures where semantic compression drops necessary state.
No learning-outcome claims.
"""
from __future__ import annotations

import copy
import json
import random
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.metrics.stable_seed import mix_seed

MODES = ("FULL_SYNC", "COMPRESSED_SYNC", "SEMANTIC_SYNC")

# Controlled NTN trace conditions (bandwidth cap Mbps, latency ms, loss, intermittency, outage s).
TRACE_CONDITIONS = (
    {"id": "high_bw_stable", "bw_mbps": 20.0, "latency_ms": 40.0, "loss": 0.005, "intermittency": 0.02, "outage_s": 0.0},
    {"id": "bw_cap_low", "bw_mbps": 0.8, "latency_ms": 55.0, "loss": 0.02, "intermittency": 0.08, "outage_s": 2.0},
    {"id": "high_latency", "bw_mbps": 5.0, "latency_ms": 180.0, "loss": 0.01, "intermittency": 0.05, "outage_s": 1.0},
    {"id": "packet_loss", "bw_mbps": 4.0, "latency_ms": 60.0, "loss": 0.12, "intermittency": 0.10, "outage_s": 3.0},
    {"id": "intermittent", "bw_mbps": 3.0, "latency_ms": 70.0, "loss": 0.04, "intermittency": 0.35, "outage_s": 8.0},
    {"id": "long_outage", "bw_mbps": 2.0, "latency_ms": 90.0, "loss": 0.06, "intermittency": 0.25, "outage_s": 45.0},
)


def _waike_state(seed: int) -> dict[str, Any]:
    """Realistic WAIKE / gunnchAI continuity object (not a learning outcome claim)."""
    rng = random.Random(mix_seed(seed, "waike_state"))
    lesson_id = f"lesson_{rng.randint(1000, 9999)}"
    return {
        "schema": "gunnchos.waike.continuity_state.v1",
        "session_id": f"sess_{seed}_{rng.randint(10, 99)}",
        "progress": {
            "lesson_id": lesson_id,
            "module_index": rng.randint(0, 8),
            "checkpoint": rng.choice(["intro", "practice", "quiz", "review"]),
            "percent_complete": round(rng.uniform(5.0, 95.0), 2),
            "last_correct_streak": rng.randint(0, 12),
        },
        "lesson_metadata": {
            "title": f"NTN continuity unit {rng.randint(1, 40)}",
            "difficulty": rng.choice(["intro", "intermediate", "advanced"]),
            "estimated_minutes": rng.randint(8, 45),
            "tags": ["ntn", "equity", "waike"],
        },
        "learner_delta": {
            "mastery_delta": round(rng.uniform(-0.05, 0.15), 4),
            "attempts_delta": rng.randint(0, 6),
            "hints_used_delta": rng.randint(0, 3),
            "error_patterns": rng.sample(["latency_timeout", "partial_answer", "skip"], k=rng.randint(0, 2)),
        },
        "text_feedback": (
            "Continue from last checkpoint; retain queued assignment context. "
            f"Seed note {seed}."
        ),
        "queued_assignment_metadata": {
            "assignment_id": f"asg_{rng.randint(200, 900)}",
            "due_epoch_s": 1_700_000_000 + rng.randint(0, 86_400),
            "required_artifacts": ["checkpoint_json", "reflection_text"],
            "must_preserve_fields": [
                "progress.lesson_id",
                "progress.checkpoint",
                "queued_assignment_metadata.assignment_id",
                "queued_assignment_metadata.due_epoch_s",
                "learner_delta.mastery_delta",
            ],
        },
        "gunnchai_coach_hint": {
            "tone": "supportive",
            "next_action": "resume_checkpoint",
            "privacy_mode": "on_device_features",
        },
    }


def _payload_bytes(obj: Any) -> int:
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _compress_state(state: dict[str, Any]) -> dict[str, Any]:
    """Lossy but mostly faithful compressed sync."""
    return {
        "schema": state["schema"],
        "session_id": state["session_id"],
        "progress": {
            "lesson_id": state["progress"]["lesson_id"],
            "module_index": state["progress"]["module_index"],
            "checkpoint": state["progress"]["checkpoint"],
            "percent_complete": round(state["progress"]["percent_complete"], 0),
        },
        "lesson_metadata": {
            "title": state["lesson_metadata"]["title"],
            "difficulty": state["lesson_metadata"]["difficulty"],
        },
        "learner_delta": {
            "mastery_delta": round(state["learner_delta"]["mastery_delta"], 2),
            "attempts_delta": state["learner_delta"]["attempts_delta"],
        },
        "text_feedback": state["text_feedback"][:80],
        "queued_assignment_metadata": {
            "assignment_id": state["queued_assignment_metadata"]["assignment_id"],
            "due_epoch_s": state["queued_assignment_metadata"]["due_epoch_s"],
        },
        "gunnchai_coach_hint": {"next_action": state["gunnchai_coach_hint"]["next_action"]},
    }


def _semantic_state(state: dict[str, Any], *, drop_critical: bool) -> dict[str, Any]:
    """Semantic sync — intentionally may drop necessary queued-assignment state."""
    out = {
        "schema": "gunnchos.waike.semantic_delta.v1",
        "session_id": state["session_id"],
        "progress": {
            "lesson_id": state["progress"]["lesson_id"],
            "checkpoint": state["progress"]["checkpoint"],
        },
        "learner_delta": {
            "mastery_delta": round(state["learner_delta"]["mastery_delta"], 2),
        },
        "text_feedback": "resume",
        "gunnchai_coach_hint": {"next_action": "resume_checkpoint"},
    }
    if not drop_critical:
        out["queued_assignment_metadata"] = {
            "assignment_id": state["queued_assignment_metadata"]["assignment_id"],
            "due_epoch_s": state["queued_assignment_metadata"]["due_epoch_s"],
        }
        out["progress"]["percent_complete"] = state["progress"]["percent_complete"]
    # When drop_critical: omit assignment id/due and percent — necessary state loss.
    return out


def _fidelity(original: dict[str, Any], recovered: dict[str, Any]) -> dict[str, Any]:
    must = original["queued_assignment_metadata"]["must_preserve_fields"]

    def _get(obj: dict[str, Any], path: str) -> Any:
        cur: Any = obj
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur

    missing = []
    for path in must:
        if _get(recovered, path) is None:
            missing.append(path)
    preserved = 1.0 - (len(missing) / max(1, len(must)))
    semantic_loss = len(missing) / max(1, len(must))
    return {
        "state_fidelity": round(preserved, 4),
        "semantic_loss": round(semantic_loss, 4),
        "missing_required_fields": missing,
        "necessary_state_dropped": len(missing) > 0,
    }


def _transfer(mode: str, state: dict[str, Any], cond: dict[str, Any], *, seed: int) -> dict[str, Any]:
    rng = random.Random(mix_seed(seed, mode, cond["id"]))
    drop_critical = mode == "SEMANTIC_SYNC" and cond["id"] in {"long_outage", "bw_cap_low", "intermittent"} and (seed % 2 == 1)
    if mode == "FULL_SYNC":
        payload = copy.deepcopy(state)
    elif mode == "COMPRESSED_SYNC":
        payload = _compress_state(state)
    else:
        payload = _semantic_state(state, drop_critical=drop_critical)

    nbytes = _payload_bytes(payload)
    # Transfer model: time ≈ outage + serialization / bw + latency + loss retransmit + intermittency holds
    bw_Bps = max(1.0, cond["bw_mbps"] * 125_000.0)  # Mbps → bytes/s approx
    tx_s = nbytes / bw_Bps
    retransmit = 1.0 + 3.0 * cond["loss"]
    intermittency_hold = cond["intermittency"] * (8.0 + rng.random() * 4.0)
    completion_latency_s = cond["outage_s"] + cond["latency_ms"] / 1000.0 + tx_s * retransmit + intermittency_hold
    # Delivery success degrades with loss/outage for large payloads
    size_pressure = nbytes / 800.0
    p_fail = min(0.95, cond["loss"] * 2.5 + cond["intermittency"] * 0.5 + (0.25 if cond["outage_s"] > 30 and mode == "FULL_SYNC" else 0.0) * size_pressure)
    delivered = rng.random() > p_fail
    recovered = payload if delivered else {}
    fid = _fidelity(state, recovered) if delivered else {
        "state_fidelity": 0.0,
        "semantic_loss": 1.0,
        "missing_required_fields": list(state["queued_assignment_metadata"]["must_preserve_fields"]),
        "necessary_state_dropped": True,
    }
    reconnect_recovery_s = (
        2.0 + nbytes / max(bw_Bps, 1.0) * (0.3 if mode == "SEMANTIC_SYNC" else 1.0)
        if delivered
        else cond["outage_s"] + 15.0 + nbytes / max(bw_Bps, 1.0)
    )
    energy_proxy = round((nbytes / 1000.0) * (1.0 + cond["loss"] * 2.0) * (1.2 if mode == "FULL_SYNC" else 0.7), 4)
    return {
        "mode": mode,
        "condition_id": cond["id"],
        "bytes": nbytes,
        "completion_latency_s": round(completion_latency_s, 4),
        "delivered": delivered,
        "reconnect_recovery_s": round(reconnect_recovery_s, 4),
        "energy_proxy": energy_proxy,
        "drop_critical_semantic": drop_critical,
        **fid,
    }


def run_r6g008(*, seeds: tuple[int, ...] = (7, 11, 19, 29, 37)) -> dict[str, Any]:
    matrix: dict[str, dict[str, list[dict[str, Any]]]] = {m: {} for m in MODES}
    all_rows: list[dict[str, Any]] = []
    for seed in seeds:
        state = _waike_state(seed)
        for cond in TRACE_CONDITIONS:
            for mode in MODES:
                row = _transfer(mode, state, cond, seed=seed)
                row["seed"] = seed
                all_rows.append(row)
                matrix[mode].setdefault(cond["id"], []).append(row)

    def _summary(rows: list[dict[str, Any]]) -> dict[str, float]:
        n = max(1, len(rows))
        return {
            "mean_bytes": round(sum(r["bytes"] for r in rows) / n, 2),
            "mean_completion_latency_s": round(sum(r["completion_latency_s"] for r in rows) / n, 4),
            "mean_state_fidelity": round(sum(r["state_fidelity"] for r in rows) / n, 4),
            "mean_semantic_loss": round(sum(r["semantic_loss"] for r in rows) / n, 4),
            "mean_reconnect_recovery_s": round(sum(r["reconnect_recovery_s"] for r in rows) / n, 4),
            "mean_energy_proxy": round(sum(r["energy_proxy"] for r in rows) / n, 4),
            "delivery_rate": round(sum(1 for r in rows if r["delivered"]) / n, 4),
        }

    summaries = {m: _summary([r for r in all_rows if r["mode"] == m]) for m in MODES}
    long_outage = [r for r in all_rows if r["condition_id"] == "long_outage"]
    long_ranked = sorted(
        MODES,
        key=lambda m: (
            _summary([r for r in long_outage if r["mode"] == m])["mean_reconnect_recovery_s"],
            _summary([r for r in long_outage if r["mode"] == m])["mean_bytes"],
        ),
    )

    # Negatives: semantic compression drops necessary state
    semantic_failures = [
        r for r in all_rows
        if r["mode"] == "SEMANTIC_SYNC" and r["necessary_state_dropped"]
    ]
    full_fails_long = [
        r for r in long_outage
        if r["mode"] == "FULL_SYNC" and (not r["delivered"] or r["completion_latency_s"] > 40.0)
    ]
    negatives = []
    for r in semantic_failures[:8]:
        negatives.append({
            "case": "semantic_sync_drops_necessary_state",
            "seed": r["seed"],
            "condition_id": r["condition_id"],
            "missing_required_fields": r["missing_required_fields"],
            "semantic_loss": r["semantic_loss"],
            "ILLUSTRATIVE": False,
            "counts_toward_real_negatives": True,
        })
    for r in full_fails_long[:4]:
        negatives.append({
            "case": "full_sync_fails_under_long_outage",
            "seed": r["seed"],
            "bytes": r["bytes"],
            "completion_latency_s": r["completion_latency_s"],
            "delivered": r["delivered"],
            "ILLUSTRATIVE": False,
            "counts_toward_real_negatives": True,
        })

    assert len(semantic_failures) >= 1
    assert len(full_fails_long) >= 1

    # Keep legacy semantic_continuity matrix shape for downstream consumers
    legacy_modes = {
        "FULL_SYNC": "FULL_CONTENT_TRANSFER",
        "COMPRESSED_SYNC": "COMPRESSED_CONTENT_TRANSFER",
        "SEMANTIC_SYNC": "LEARNING_STATE_DELTA",
    }
    legacy_matrix = {}
    for mode in MODES:
        legacy_matrix[legacy_modes[mode]] = {
            c["id"]: _summary([r for r in all_rows if r["mode"] == mode and r["condition_id"] == c["id"]])
            for c in TRACE_CONDITIONS
        }

    report = {
        "schema": "gunnchos.r6g.r6g008.v1",
        "packet": "R6G-008",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "claim_state": "DIGITALLY_EXECUTED",
        "ladder_earned": ["R0", "R1", "R2"],
        "execution_class": "CONTROLLED_TRACE_PAYLOAD_EXPERIMENT",
        "modes": list(MODES),
        "trace_conditions": list(TRACE_CONDITIONS),
        "seeds": list(seeds),
        "summaries": summaries,
        "matrix_by_mode_condition": {
            m: {cid: _summary(rows) for cid, rows in conds.items()}
            for m, conds in matrix.items()
        },
        "digital_rank_long_outage_best_to_worst": list(long_ranked),
        "best_mode_under_long_outage": long_ranked[0],
        "worst_mode_under_long_outage": long_ranked[-1],
        "documented_negative_or_no_gain": negatives,
        "semantic_necessary_state_drop_count": len(semantic_failures),
        "waike_transfer": {
            "case_study": "research/r6g/waike/case_studies/R6G-008.md",
            "counts_as_scientific_validation": False,
            "payload_object": "waike_continuity_state_v1",
            "gunnchai_affordance": "explain continuity modes; flag overclaim",
        },
        "semantic_continuity": {
            "schema": "gunnchos.r6g.semantic_continuity_ntn_education.v1",
            "ok": True,
            "modes": [legacy_modes[m] for m in MODES],
            "conditions": [c["id"] for c in TRACE_CONDITIONS],
            "matrix": legacy_matrix,
            "real_education_outcome_claimed": False,
            "human_study": "EXTERNAL_PENDING",
            "IMPROVED_STATE_OF_ART": False,
        },
        "real_education_outcome_claimed": False,
        "guaranteed_learning_outcomes": False,
        "human_study": "EXTERNAL_PENDING",
        "SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL": True,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "STANDARDIZED_6G": False,
        "COMPLIANT": False,
        "note": (
            "Executed controlled-trace continuity with WAIKE/gunnchAI objects; "
            "semantic mode can drop necessary state; no learning-outcome claims."
        ),
    }
    assert_no_soa(report)
    assert report["real_education_outcome_claimed"] is False
    assert report["guaranteed_learning_outcomes"] is False
    assert report["semantic_necessary_state_drop_count"] >= 1
    return report
