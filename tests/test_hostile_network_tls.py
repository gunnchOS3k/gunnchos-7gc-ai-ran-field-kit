"""Hostile-network TLS fixture portability + real verification failures."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509

from net_sec_rc001.hostile_network import (
    LocalHostileRuntime,
    generate_hostile_tls_fixtures,
    run_hostile_network_digital,
)

ROOT = Path(__file__).resolve().parents[1]
HOSTILE_SRC = ROOT / "net_sec_rc001" / "hostile_network.py"

FORBIDDEN_OPENSSL_DATE_FLAGS = ("-not_before", "-not_after")


def test_hostile_source_forbids_openssl_date_flags():
    """Regression: OpenSSL CLI date flags are non-portable on GitHub runners."""
    src = HOSTILE_SRC.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert node.value not in FORBIDDEN_OPENSSL_DATE_FLAGS, (
                f"forbidden OpenSSL flag literal {node.value!r} in hostile_network.py"
            )
    assert '["openssl"' not in src and "['openssl'" not in src
    assert "subprocess.run" not in src
    assert "subprocess.call" not in src
    assert "generate_hostile_tls_fixtures" in src
    assert "from cryptography" in src


def test_cryptography_fixtures_have_deterministic_windows(tmp_path: Path):
    fixtures = generate_hostile_tls_fixtures(tmp_path)
    ca = x509.load_pem_x509_certificate(fixtures["ca"].read_bytes())
    valid = x509.load_pem_x509_certificate(fixtures["cert"].read_bytes())
    mismatch = x509.load_pem_x509_certificate(fixtures["mismatch"].read_bytes())
    expired = x509.load_pem_x509_certificate(fixtures["expired"].read_bytes())

    assert ca.subject == ca.issuer
    assert valid.issuer == ca.subject
    assert mismatch.issuer == ca.subject
    assert expired.issuer == ca.subject

    # Fixed windows from module constants
    assert fixtures["valid_not_before"] == "2026-08-14T12:00:00+00:00"
    assert fixtures["valid_not_after"] == "2027-08-15T12:00:00+00:00"
    assert fixtures["expired_not_before"] == "2020-01-01T00:00:00+00:00"
    assert fixtures["expired_not_after"] == "2020-01-02T00:00:00+00:00"

    now = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert expired.not_valid_after_utc < now
    assert valid.not_valid_before_utc <= now <= valid.not_valid_after_utc


def test_tls_mismatch_and_expired_actually_fail_verification():
    rt = LocalHostileRuntime()
    try:
        certs = rt._make_certs()
        ca = certs["ca"]

        ok_port = rt.start_tls_server(certs["cert"], certs["key"])
        ok = rt.tls_client_probe(ok_port, server_hostname="updates.gunnchos.local", cafile=ca)
        assert ok["ok"] is True, ok

        bad_port = rt.start_tls_server(certs["mismatch"], certs["mismatch_key"])
        bad = rt.tls_client_probe(bad_port, server_hostname="updates.gunnchos.local", cafile=ca)
        assert bad["ok"] is False, bad
        assert bad["reason"] == "tls_error"

        exp_port = rt.start_tls_server(certs["expired"], certs["expired_key"])
        exp = rt.tls_client_probe(exp_port, server_hostname="updates.gunnchos.local", cafile=ca)
        assert exp["ok"] is False, exp
        assert exp["reason"] == "tls_error"
    finally:
        rt.stop_tls_server()


def test_run_hostile_network_digital_ok_without_openssl_cli():
    report = run_hostile_network_digital()
    assert report["ok"] is True
    assert report["uncontrolled_external_attack"] is False
    by_id = {c["case_id"]: c for c in report["cases"]}
    assert by_id["HN-TLS-SOCKET-001"]["passed"] is True
    assert by_id["HN-TLS-SOCKET-NEG-MISMATCH-001"]["passed"] is True
    assert by_id["HN-TLS-SOCKET-NEG-EXPIRED-001"]["passed"] is True
