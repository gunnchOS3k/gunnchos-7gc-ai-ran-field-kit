"""Actuation firewall. Default real actuation is disabled."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

REAL_ACTUATION_ENV = "REAL_ACTUATION_ENABLED"
BROWSER_PATHS = {"browser", "browser_direct", "mlv_browser"}


def real_actuation_enabled() -> bool:
    raw = os.environ.get(REAL_ACTUATION_ENV, "false").strip().lower()
    return raw in {"1", "true", "yes"}


def evaluate_request(request: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "authenticated": bool((request.get("identity") or {}).get("authenticated")),
        "authorized_role": request.get("role") in {"researcher", "testbed_operator", "auditor", "system"},
        "explicit_testbed": bool((request.get("testbed") or {}).get("explicit")),
        "allowlisted_action": bool((request.get("action") or {}).get("allowlisted")),
        "numeric_bounds": bool((request.get("numeric_bounds") or {}).get("within_bounds")),
        "ttl_present": int(request.get("ttl_s") or 0) > 0,
        "regulatory_band": bool((request.get("regulatory") or {}).get("band_allowed")),
        "rate_limit": bool((request.get("rate_limit") or {}).get("within_limit")),
        "dry_run": bool(request.get("dry_run")),
        "rollback_supported": bool((request.get("rollback") or {}).get("supported")),
        "not_browser_direct": request.get("source_path") not in BROWSER_PATHS,
        "real_actuation_disabled": not real_actuation_enabled(),
    }
    source = request.get("source_path")
    if source in BROWSER_PATHS:
        decision = "denied"
        reason = "browser-direct actuation path is forbidden"
        applied = False
    elif not all(
        checks[k]
        for k in (
            "authenticated",
            "authorized_role",
            "explicit_testbed",
            "allowlisted_action",
            "numeric_bounds",
            "ttl_present",
            "regulatory_band",
            "rate_limit",
            "rollback_supported",
            "not_browser_direct",
        )
    ):
        decision = "denied"
        reason = "request failed firewall validation"
        applied = False
    elif not real_actuation_enabled():
        decision = "dry_run_recorded" if request.get("dry_run") else "denied"
        reason = "REAL_ACTUATION_ENABLED=false; no physical control"
        applied = False
    else:
        # Authorized testbed path remains a contract target, not a claim.
        decision = "shadow_recorded"
        reason = "real actuation flag set but E2/testbed apply is not implemented"
        applied = False

    return {
        "schema_name": "gunnchos.ran_actuation_receipt",
        "schema_version": "1.0.0",
        "run_id": request.get("run_id", "unknown"),
        "site_id": request.get("site_id", "unknown"),
        "request_id": request.get("request_id", "unknown00"),
        "decision": decision,
        "real_actuation_enabled": real_actuation_enabled(),
        "e2_claimed": False,
        "applied": applied,
        "reason": reason,
        "audit": {
            "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "checks": checks,
        },
        "producer": request.get("producer")
        or {
            "repository": "gunnchos-7gc-ai-ran-field-kit",
            "commit": "0" * 40,
        },
    }
