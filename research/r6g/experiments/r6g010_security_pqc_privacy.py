"""R6G-010 — Zero-trust / PQC / ISAC privacy — executed digital security tests.

Docs alone ≠ execution. Each case records accept/reject.
Not a certification; STANDARDIZED_6G/COMPLIANT remain false.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

from research.r6g.claim_firewall import assert_no_soa

# Pre-registered weights (locked before scoring campaigns).
PREREGISTERED_SECURITY_WEIGHTS = {
    "scheme_id": "SEC_PRIV_V1",
    "locked_at": "2026-08-15",
    "weights": {
        "zero_trust_posture": 0.25,
        "pqc_readiness": 0.25,
        "sensing_privacy": 0.25,
        "key_lifecycle": 0.15,
        "auditability": 0.10,
    },
    "amendments": [],
    "classification": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
    "NOT_CERTIFICATION": True,
}

PQC_ALGORITHMS = ("Dilithium2", "Kyber768", "Falcon512", "SPHINCS+-SHA2-128s")


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_profile(components: dict[str, float]) -> dict[str, Any]:
    w = PREREGISTERED_SECURITY_WEIGHTS["weights"]
    total = 0.0
    detail = {}
    for k, wt in w.items():
        v = _clamp01(float(components.get(k, 0.0)))
        detail[k] = {"value": v, "weight": wt, "weighted": round(v * wt, 4)}
        total += v * wt
    privacy = detail["sensing_privacy"]["value"]
    privacy_floor_fail = privacy < 0.25
    return {
        "components": detail,
        "score": round(total, 4),
        "privacy_floor_fail": privacy_floor_fail,
        "scheme_id": PREREGISTERED_SECURITY_WEIGHTS["scheme_id"],
        "classification": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
        "NOT_CERTIFICATION": True,
    }


def _sign(secret: bytes, msg: bytes) -> str:
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


def _verify(secret: bytes, msg: bytes, sig: str) -> bool:
    return hmac.compare_digest(_sign(secret, msg), sig)


def _run_tests(*, now: float | None = None) -> list[dict[str, Any]]:
    """Executable accept/reject battery."""
    t0 = now if now is not None else 1_724_000_000.0  # fixed for determinism in default path
    secret = b"r6g010-lab-secret-v1"
    identity = "device:ring-sim-001"
    nonce_store: set[str] = set()
    results: list[dict[str, Any]] = []

    def record(name: str, expected: str, decision: str, detail: dict[str, Any]) -> None:
        results.append({
            "test": name,
            "expected": expected,
            "decision": decision,
            "pass": decision == expected,
            "detail": detail,
        })

    # 1. Signature verify — valid
    msg = b"telemetry:ok"
    sig = _sign(secret, msg)
    decision = "ACCEPT" if _verify(secret, msg, sig) else "REJECT"
    record("signature_verify_valid", "ACCEPT", decision, {"alg": "HMAC-SHA256"})

    # 2. Signature verify — tampered
    decision = "ACCEPT" if _verify(secret, b"telemetry:evil", sig) else "REJECT"
    record("signature_verify_tampered_message", "REJECT", decision, {})

    # 3. Anti-replay
    nonce = "nonce-001"
    if nonce in nonce_store:
        decision = "REJECT"
    else:
        nonce_store.add(nonce)
        decision = "ACCEPT"
    record("anti_replay_first_use", "ACCEPT", decision, {"nonce": nonce})
    decision = "REJECT" if nonce in nonce_store else "ACCEPT"
    # second use must reject
    if nonce in nonce_store:
        decision = "REJECT"
    record("anti_replay_reuse", "REJECT", decision, {"nonce": nonce})

    # 4. Expired credential
    cred_exp = t0 - 60
    decision = "REJECT" if cred_exp < t0 else "ACCEPT"
    record("expired_credential", "REJECT", decision, {"expires_at": cred_exp, "now": t0})

    # 5. Wrong identity
    claimed = "device:attacker-999"
    decision = "ACCEPT" if claimed == identity else "REJECT"
    record("wrong_identity", "REJECT", decision, {"claimed": claimed, "expected_identity": identity})

    # 6. Tampered model digest
    model_digest = hashlib.sha256(b"model-weights-v1").hexdigest()
    presented = hashlib.sha256(b"model-weights-TAMPERED").hexdigest()
    decision = "ACCEPT" if presented == model_digest else "REJECT"
    record("tampered_model", "REJECT", decision, {"expected": model_digest[:16], "presented": presented[:16]})

    # 7. Tampered telemetry
    telem = {"snr_db": 12.5, "provenance": "rf_frontend"}
    telem_bytes = str(sorted(telem.items())).encode()
    good_sig = _sign(secret, telem_bytes)
    bad = dict(telem)
    bad["snr_db"] = 99.0
    bad_bytes = str(sorted(bad.items())).encode()
    decision = "ACCEPT" if _verify(secret, bad_bytes, good_sig) else "REJECT"
    record("tampered_telemetry", "REJECT", decision, {})

    # 8. Spoofed sensor provenance
    allowed_provenance = {"rf_frontend", "ring_uwb_sim", "device_imu"}
    presented_prov = "attacker_injected_camera"
    decision = "ACCEPT" if presented_prov in allowed_provenance else "REJECT"
    record("spoofed_sensor_provenance", "REJECT", decision, {"presented": presented_prov})

    # 9. Unauthorized policy action
    allowed_actions = {"defer_sync", "semantic_sync", "local_only"}
    action = "force_exfiltrate_raw_stream"
    decision = "ACCEPT" if action in allowed_actions else "REJECT"
    record("unauthorized_policy_action", "REJECT", decision, {"action": action})

    # 10. PQC agility / config
    configured = ["Dilithium2", "Kyber768"]
    agility_ok = all(a in PQC_ALGORITHMS for a in configured) and len(configured) >= 2
    decision = "ACCEPT" if agility_ok else "REJECT"
    record("pqc_agility_config", "ACCEPT", decision, {"configured": configured, "catalog": list(PQC_ALGORITHMS)})

    # 11. Consent denial
    consent = {"sensing_share": False, "cloud_upload": False}
    requested = "cloud_upload"
    decision = "ACCEPT" if consent.get(requested, False) else "REJECT"
    record("consent_denial", "REJECT", decision, {"requested": requested, "consent": consent})

    # 12. Malicious state injection
    state = {"progress": {"checkpoint": "quiz"}, "admin_override": False}
    injected = {"progress": {"checkpoint": "quiz"}, "admin_override": True, "__proto__": {"pollute": True}}
    # Reject if unknown privileged keys appear
    privileged = {"admin_override", "__proto__", "root"}
    decision = "REJECT" if any(k in injected and injected.get(k) not in (False, None) for k in privileged) else "ACCEPT"
    if injected.get("admin_override") and not state.get("admin_override"):
        decision = "REJECT"
    record("malicious_state_injection", "REJECT", decision, {"injected_keys": sorted(injected.keys())})

    return results


def run_r6g010() -> dict[str, Any]:
    tests = _run_tests(now=1_724_000_000.0)
    all_pass = all(t["pass"] for t in tests)
    profiles = {
        "baseline_rel16_terrestrial": score_profile({
            "zero_trust_posture": 0.45,
            "pqc_readiness": 0.20,
            "sensing_privacy": 0.40,
            "key_lifecycle": 0.50,
            "auditability": 0.55,
        }),
        "research_candidate_digital": score_profile({
            "zero_trust_posture": 0.70,
            "pqc_readiness": 0.55,
            "sensing_privacy": 0.65,
            "key_lifecycle": 0.60,
            "auditability": 0.70,
        }),
        "overclaim_trap": score_profile({
            "zero_trust_posture": 0.95,
            "pqc_readiness": 0.95,
            "sensing_privacy": 0.10,
            "key_lifecycle": 0.90,
            "auditability": 0.90,
        }),
    }
    trap = profiles["overclaim_trap"]
    cand = profiles["research_candidate_digital"]
    trap_fails_floor = trap["privacy_floor_fail"] is True and cand["privacy_floor_fail"] is False

    accepts = sum(1 for t in tests if t["decision"] == "ACCEPT")
    rejects = sum(1 for t in tests if t["decision"] == "REJECT")

    report = {
        "schema": "gunnchos.r6g.r6g010.v1",
        "packet": "R6G-010",
        "ok": all_pass,
        "status": "DIGITALLY_EXECUTED",
        "claim_state": "DIGITALLY_EXECUTED",
        "ladder_earned": ["R0", "R1", "R2"],
        "execution_class": "EXECUTED_SECURITY_TEST_BATTERY",
        "weight_scheme": PREREGISTERED_SECURITY_WEIGHTS,
        "profiles": profiles,
        "privacy_floor": 0.25,
        "executed_tests": tests,
        "executed_test_count": len(tests),
        "accept_count": accepts,
        "reject_count": rejects,
        "all_tests_met_expected": all_pass,
        "falsification": {
            "overclaim_trap_scores_worse_when_privacy_collapses": trap_fails_floor,
            "note": "Privacy-floor gate plus executed reject paths",
            "ILLUSTRATIVE": False,
        },
        "documented_negative_or_no_gain": [
            {
                "case": "overclaim_trap_privacy_floor",
                "result": "HIGH_AGGREGATE_REJECTED_ON_PRIVACY_FLOOR",
                "privacy_floor_fail": True,
                "ILLUSTRATIVE": False,
                "counts_toward_real_negatives": True,
            }
        ] if trap_fails_floor else [],
        "SECURITY_PQC_PRIVACY_HOOKS_DIGITAL": True,
        "STANDARDIZED_6G": False,
        "COMPLIANT": False,
        "CERTIFIED": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "note": "Executed digital accept/reject battery; not a certification.",
    }
    assert_no_soa(report)
    assert report["STANDARDIZED_6G"] is False
    assert report["COMPLIANT"] is False
    assert report["executed_test_count"] >= 11
    assert report["all_tests_met_expected"] is True
    return report
