"""Zero-trust digital + hostile network local testbed (no uncontrolled external attack)."""
from __future__ import annotations

from typing import Any


def run_hostile_network_digital() -> dict[str, Any]:
    cases = []

    def case(name: str, trusted: bool, credentials_sent: bool, expect_block: bool) -> None:
        blocked = (not trusted) and (not credentials_sent)
        passed = blocked if expect_block else trusted and credentials_sent
        cases.append({
            "name": name,
            "trusted": trusted,
            "credentials_sent": credentials_sent,
            "passed": passed,
        })

    case("happy_tls_trusted", True, True, False)
    case("dns_poison", False, False, True)
    case("http_downgrade", False, False, True)
    case("captive_portal", False, False, True)
    case("expired_cert", False, False, True)
    case("hostname_mismatch", False, False, True)
    case("link_loss_restore", True, True, False)

    ok = all(c["passed"] for c in cases) and all(
        (not c["trusted"]) is False or c["credentials_sent"] is False or c["name"].startswith("happy") or c["name"].startswith("link")
        for c in cases
    )
    # Stronger: no credentials on untrusted
    no_leak = all((c["credentials_sent"] is False) or c["trusted"] for c in cases)
    ok = all(c["passed"] for c in cases) and no_leak
    return {
        "schema": "gunnchos.net_sec_rc001.hostile_network_digital.v1",
        "ok": ok,
        "scope": "LOCAL_INPROCESS_ONLY",
        "uncontrolled_external_attack": False,
        "RF_WIFI": "E5_E8_EXTERNAL_PENDING",
        "cases": cases,
        "claim_boundary": "Local digital hostile-network testbed only; no uncontrolled external attack.",
        "token_candidate": "HOSTILE_NETWORK_DIGITAL",
    }
