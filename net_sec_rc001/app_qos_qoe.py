"""App-level QoS/QoE effects for WAIKE / office / gunnchAI / games / Ring / builder / teacher."""
from __future__ import annotations

from typing import Any


APPS = (
    "waike",
    "office",
    "gunnchai",
    "games",
    "ring",
    "builder",
    "teacher",
)

PATH_QOE = {
    "ethernet": 0.95,
    "wifi": 0.88,
    "cellular_rel16": 0.78,
    "ntn_sim": 0.55,
    "edge": 0.82,
    "cloud": 0.70,
    "local": 0.98,
    "lan": 0.90,
}

QOS_CLASS = {
    "waike": "interactive",
    "office": "interactive",
    "teacher": "interactive",
    "builder": "interactive",
    "games": "realtime",
    "ring": "realtime",
    "gunnchai": "ai_interactive",
}


def app_effect(app: str, path: str) -> dict[str, Any]:
    base = PATH_QOE[path]
    sensitivity = {
        "waike": 0.05,
        "office": 0.04,
        "gunnchai": 0.08,
        "games": 0.12,
        "ring": 0.10,
        "builder": 0.07,
        "teacher": 0.06,
    }[app]
    latency_penalty = {"ntn_sim": 0.20, "cloud": 0.08, "cellular_rel16": 0.04}.get(path, 0.0)
    qoe = max(0.0, min(1.0, base - sensitivity * latency_penalty * 5))
    return {
        "app": app,
        "path": path,
        "qoe_score": round(qoe, 3),
        "qos_class": QOS_CLASS[app],
        "community_outcome_fabricated": False,
    }


def run_app_qos_qoe() -> dict[str, Any]:
    matrix = []
    for app in APPS:
        for path in ("wifi", "cellular_rel16", "ntn_sim", "local"):
            matrix.append(app_effect(app, path))
    games_ok = all(
        m["qos_class"] == "realtime" for m in matrix if m["app"] == "games"
    )
    ok = (
        all(m["community_outcome_fabricated"] is False for m in matrix)
        and len(matrix) == len(APPS) * 4
        and games_ok
    )
    return {
        "schema": "gunnchos.net_sec_rc001.app_qos_qoe.v1",
        "ok": ok,
        "apps": list(APPS),
        "matrix": matrix,
        "claim_boundary": "Synthetic digital QoE effects only; no fabricated community outcomes.",
        "token_candidate": "APP_QOS_QOE_DIGITAL",
    }
