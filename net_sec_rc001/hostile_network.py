"""Zero-trust digital hostile-network local testbed.

Hits a real local runtime: loopback TCP/TLS socket, in-process DNS policy,
credential vault, and coupling to Rel-16 terrestrial + service-continuity
failover. No uncontrolled external attack. No RF field claim.

TLS fixtures are generated with the ``cryptography`` library (portable PEM
issuance). Do not use OpenSSL CLI absolute-date generation flags on this path —
those flags are non-portable across runner OpenSSL builds.
"""
from __future__ import annotations

import ipaddress
import socket
import ssl
import tempfile
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from .service_continuity import select_path
from .terrestrial_rel16 import RM520NTerrestrialDigital


EVIDENCE_LEVEL = "E4_DIGITAL_LOCAL_RUNTIME"
RF_WIFI_STATUS = "E5_E8_EXTERNAL_PENDING"

# Deterministic validity windows (fixed epoch — not wall-clock dependent).
_FIXED_NOW = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
_VALID_NOT_BEFORE = _FIXED_NOW - timedelta(days=1)
_VALID_NOT_AFTER = _FIXED_NOW + timedelta(days=365)
_EXPIRED_NOT_BEFORE = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
_EXPIRED_NOT_AFTER = datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc)


def _write_key(path: Path, key: rsa.RSAPrivateKey) -> None:
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def _write_cert(path: Path, cert: x509.Certificate) -> None:
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def _build_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _name(cn: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def _sign_cert(
    *,
    subject: x509.Name,
    issuer: x509.Name,
    public_key: rsa.RSAPublicKey,
    signer_key: rsa.RSAPrivateKey,
    not_before: datetime,
    not_after: datetime,
    is_ca: bool = False,
    san: x509.SubjectAlternativeName | None = None,
    serial: int,
) -> x509.Certificate:
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(serial)
        .not_valid_before(not_before)
        .not_valid_after(not_after)
    )
    if is_ca:
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,
        )
    if san is not None:
        builder = builder.add_extension(san, critical=False)
    return builder.sign(private_key=signer_key, algorithm=hashes.SHA256())


def generate_hostile_tls_fixtures(root: Path) -> dict[str, Path]:
    """Create CA + valid / hostname-mismatch / expired leaf certs under ``root``.

    Deterministic validity windows; PEM material only. No OpenSSL CLI date flags.
    """
    root.mkdir(parents=True, exist_ok=True)

    ca_key = _build_key()
    ca_cert = _sign_cert(
        subject=_name("gunnchos-hostile-test-ca"),
        issuer=_name("gunnchos-hostile-test-ca"),
        public_key=ca_key.public_key(),
        signer_key=ca_key,
        not_before=_VALID_NOT_BEFORE,
        not_after=_VALID_NOT_AFTER,
        is_ca=True,
        serial=1,
    )
    ca_path = root / "ca.crt"
    ca_key_path = root / "ca.key"
    _write_cert(ca_path, ca_cert)
    _write_key(ca_key_path, ca_key)

    # Valid leaf for updates.gunnchos.local (+ SAN)
    server_key = _build_key()
    server_cert = _sign_cert(
        subject=_name("updates.gunnchos.local"),
        issuer=ca_cert.subject,
        public_key=server_key.public_key(),
        signer_key=ca_key,
        not_before=_VALID_NOT_BEFORE,
        not_after=_VALID_NOT_AFTER,
        san=x509.SubjectAlternativeName(
            [
                x509.DNSName("updates.gunnchos.local"),
                x509.DNSName("api.gunnchos.local"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]
        ),
        serial=2,
    )
    key = root / "server.key"
    cert = root / "server.crt"
    _write_key(key, server_key)
    _write_cert(cert, server_cert)

    # Hostname mismatch leaf (evil CN), still signed by same CA
    evil_key = _build_key()
    evil_cert = _sign_cert(
        subject=_name("evil.example"),
        issuer=ca_cert.subject,
        public_key=evil_key.public_key(),
        signer_key=ca_key,
        not_before=_VALID_NOT_BEFORE,
        not_after=_VALID_NOT_AFTER,
        san=x509.SubjectAlternativeName([x509.DNSName("evil.example")]),
        serial=3,
    )
    bad_cert = root / "mismatch.crt"
    evil_key_path = root / "evil.key"
    _write_key(evil_key_path, evil_key)
    _write_cert(bad_cert, evil_cert)

    # Expired leaf for updates.gunnchos.local (past not_after)
    exp_key = _build_key()
    exp_cert = _sign_cert(
        subject=_name("updates.gunnchos.local"),
        issuer=ca_cert.subject,
        public_key=exp_key.public_key(),
        signer_key=ca_key,
        not_before=_EXPIRED_NOT_BEFORE,
        not_after=_EXPIRED_NOT_AFTER,
        san=x509.SubjectAlternativeName(
            [
                x509.DNSName("updates.gunnchos.local"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]
        ),
        serial=4,
    )
    expired_cert = root / "expired.crt"
    exp_key_path = root / "exp.key"
    _write_key(exp_key_path, exp_key)
    _write_cert(expired_cert, exp_cert)

    return {
        "ca": ca_path,
        "ca_key": ca_key_path,
        "key": key,
        "cert": cert,
        "mismatch": bad_cert,
        "mismatch_key": evil_key_path,
        "expired": expired_cert,
        "expired_key": exp_key_path,
        "valid_not_before": _VALID_NOT_BEFORE.isoformat(),
        "valid_not_after": _VALID_NOT_AFTER.isoformat(),
        "expired_not_before": _EXPIRED_NOT_BEFORE.isoformat(),
        "expired_not_after": _EXPIRED_NOT_AFTER.isoformat(),
    }


@dataclass
class CredentialVault:
    bearer_token: str = "dev-session-token-KEEP"
    sent_to: list[dict[str, Any]] = field(default_factory=list)

    def authorize(self, origin: str, *, trusted: bool) -> dict[str, Any]:
        if not trusted:
            self.sent_to.append({"origin": origin, "credentials_sent": False, "reason": "untrusted_origin"})
            return {"authorized": False, "credentials_sent": False, "reason": "untrusted_origin"}
        self.sent_to.append({"origin": origin, "credentials_sent": True})
        return {
            "authorized": True,
            "credentials_sent": True,
            "authorization": f"Bearer {self.bearer_token}",
        }


@dataclass
class LocalHostileRuntime:
    """In-process DNS/TLS/socket policy runtime bound to loopback only."""

    trusted_hostnames: set[str] = field(
        default_factory=lambda: {"updates.gunnchos.local", "api.gunnchos.local"}
    )
    trusted_dns: dict[str, str] = field(
        default_factory=lambda: {
            "updates.gunnchos.local": "127.0.0.1",
            "api.gunnchos.local": "127.0.0.1",
        }
    )
    vault: CredentialVault = field(default_factory=CredentialVault)
    link_up: bool = True
    events: list[dict[str, Any]] = field(default_factory=list)
    _tls_dir: Path | None = None
    _server_sock: socket.socket | None = None
    _server_thread: threading.Thread | None = None
    _stop: threading.Event = field(default_factory=threading.Event)

    def _event(self, kind: str, **kwargs: Any) -> dict[str, Any]:
        ev = {"kind": kind, **kwargs}
        self.events.append(ev)
        return ev

    def resolve_dns(self, hostname: str, *, poisoned: dict[str, str] | None = None) -> dict[str, Any]:
        table = dict(self.trusted_dns)
        if poisoned:
            table.update(poisoned)
        ip = table.get(hostname)
        if ip is None:
            self._event("dns_nxdomain", hostname=hostname)
            return {"ok": False, "reason": "nxdomain", "hostname": hostname}
        trusted_ip = self.trusted_dns.get(hostname)
        if trusted_ip is not None and ip != trusted_ip:
            self._event("dns_poison", hostname=hostname, resolved=ip, expected=trusted_ip)
            return {
                "ok": False,
                "reason": "malicious_dns",
                "hostname": hostname,
                "resolved": ip,
                "trusted": False,
            }
        try:
            addr = ipaddress.ip_address(ip)
            if not (addr.is_loopback or addr.is_private):
                return {"ok": False, "reason": "non_local_ip_forbidden", "hostname": hostname, "resolved": ip}
        except ValueError:
            return {"ok": False, "reason": "bad_ip", "hostname": hostname}
        return {"ok": True, "hostname": hostname, "resolved": ip, "trusted": True}

    def classify_origin(self, url: str, *, resolved_ip: str | None = None) -> dict[str, Any]:
        parsed = urlparse(url)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        if scheme == "http":
            return {"trusted": False, "reason": "http_downgrade", "hostname": host, "scheme": scheme}
        if scheme != "https":
            return {"trusted": False, "reason": "unsupported_scheme", "hostname": host}
        if host not in self.trusted_hostnames:
            return {"trusted": False, "reason": "untrusted_hostname", "hostname": host}
        if resolved_ip:
            expected = self.trusted_dns.get(host)
            if expected and resolved_ip != expected:
                return {
                    "trusted": False,
                    "reason": "dns_ip_mismatch",
                    "hostname": host,
                    "resolved_ip": resolved_ip,
                }
        return {"trusted": True, "hostname": host, "scheme": scheme}

    def request(
        self,
        url: str,
        *,
        with_credentials: bool = True,
        resolved_ip: str | None = None,
        tls_status: str = "ok",
        captive_portal: bool = False,
    ) -> dict[str, Any]:
        if not self.link_up:
            self._event("offline", url=url)
            return {"ok": False, "reason": "link_down", "credentials_sent": False}

        if captive_portal:
            auth = self.vault.authorize(url, trusted=False)
            self._event("captive_portal", url=url)
            return {
                "ok": False,
                "reason": "captive_portal",
                "credentials_sent": auth["credentials_sent"],
                "portal": True,
            }

        if tls_status in {"untrusted_ca", "hostname_mismatch", "expired_cert"}:
            auth = self.vault.authorize(url, trusted=False)
            reason = {
                "untrusted_ca": "untrusted_tls",
                "hostname_mismatch": "hostname_mismatch",
                "expired_cert": "expired_cert",
            }[tls_status]
            return {"ok": False, "reason": reason, "credentials_sent": auth["credentials_sent"]}

        origin = self.classify_origin(url, resolved_ip=resolved_ip)
        if not origin["trusted"]:
            auth = self.vault.authorize(url, trusted=False)
            return {
                "ok": False,
                "reason": origin["reason"],
                "credentials_sent": auth["credentials_sent"],
                "origin": origin,
            }

        auth = (
            self.vault.authorize(url, trusted=True)
            if with_credentials
            else {"credentials_sent": False, "authorized": False}
        )
        self._event("trusted_request", url=url)
        return {
            "ok": True,
            "reason": "ok",
            "credentials_sent": bool(auth.get("credentials_sent")),
            "origin": origin,
        }

    def set_link(self, up: bool) -> dict[str, Any]:
        self.link_up = up
        return self._event("link", up=up)

    def _make_certs(self) -> dict[str, Path]:
        root = Path(tempfile.mkdtemp(prefix="netsec-hostile-tls-"))
        self._tls_dir = root
        return generate_hostile_tls_fixtures(root)

    def start_tls_server(self, cert: Path, key: Path) -> int:
        self.stop_tls_server()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        sock.listen(5)
        self._server_sock = sock
        self._stop.clear()

        def _serve() -> None:
            sock.settimeout(0.2)
            while not self._stop.is_set():
                try:
                    conn, _addr = sock.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                try:
                    with ctx.wrap_socket(conn, server_side=True) as tls:
                        tls.recv(64)
                        tls.sendall(b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nOK")
                except Exception:
                    try:
                        conn.close()
                    except Exception:
                        pass

        t = threading.Thread(target=_serve, name="netsec-hostile-tls", daemon=True)
        self._server_thread = t
        t.start()
        return sock.getsockname()[1]

    def stop_tls_server(self) -> None:
        self._stop.set()
        if self._server_sock is not None:
            try:
                self._server_sock.close()
            except OSError:
                pass
            self._server_sock = None
        if self._server_thread is not None:
            self._server_thread.join(timeout=2.0)
            self._server_thread = None

    def tls_client_probe(self, port: int, *, server_hostname: str, cafile: Path | None) -> dict[str, Any]:
        ctx = ssl.create_default_context()
        if cafile is not None:
            ctx.load_verify_locations(cafile=str(cafile))
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
        else:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=2.0) as raw:
                with ctx.wrap_socket(raw, server_hostname=server_hostname) as tls:
                    tls.sendall(b"GET / HTTP/1.0\r\n\r\n")
                    data = tls.recv(128)
            return {"ok": True, "bytes": len(data), "peer": server_hostname, "loopback": True}
        except ssl.SSLError as exc:
            return {"ok": False, "reason": "tls_error", "error": str(exc), "loopback": True}
        except OSError as exc:
            return {"ok": False, "reason": "socket_error", "error": str(exc), "loopback": True}

    def couple_to_continuity_on_cellular_compromise(self) -> dict[str, Any]:
        """When Rel-16 cellular path is marked hostile, failover via continuity policy."""
        modem = RM520NTerrestrialDigital()
        modem.sim(True)
        modem.register("SA")
        modem.bearer("internet")
        modem.connect()
        available = {
            "ethernet": False,
            "wifi": True,
            "lan": False,
            "cellular_rel16": True,
            "edge": True,
            "cloud": True,
            "ntn_sim": True,
            "local": True,
        }
        dns = self.resolve_dns(
            "updates.gunnchos.local",
            poisoned={"updates.gunnchos.local": "198.51.100.66"},
        )
        if dns.get("reason") == "malicious_dns":
            available["cellular_rel16"] = False
            modem.failover("wifi")
        nxt = select_path(available)
        return {
            "dns": dns,
            "modem_path_after": modem.state.get("active_path"),
            "continuity_selected": nxt,
            "cellular_rel16_disabled": available["cellular_rel16"] is False,
            "rm520n_five_ga_claimed": False,
        }


def run_hostile_network_digital() -> dict[str, Any]:
    rt = LocalHostileRuntime()
    cases: list[dict[str, Any]] = []

    def add(case_id: str, passed: bool, evidence: dict[str, Any]) -> None:
        cases.append({"case_id": case_id, "passed": bool(passed), "evidence": evidence})

    try:
        certs = rt._make_certs()
        ca = certs["ca"]
        port = rt.start_tls_server(certs["cert"], certs["key"])

        probe = rt.tls_client_probe(port, server_hostname="updates.gunnchos.local", cafile=ca)
        add("HN-TLS-SOCKET-001", probe.get("ok") is True and probe.get("loopback") is True, probe)

        bad_port = rt.start_tls_server(certs["mismatch"], certs["mismatch_key"])
        bad_probe = rt.tls_client_probe(
            bad_port, server_hostname="updates.gunnchos.local", cafile=ca
        )
        add(
            "HN-TLS-SOCKET-NEG-MISMATCH-001",
            bad_probe.get("ok") is False and bad_probe.get("loopback") is True,
            bad_probe,
        )

        exp_port = rt.start_tls_server(certs["expired"], certs["expired_key"])
        exp_probe = rt.tls_client_probe(
            exp_port, server_hostname="updates.gunnchos.local", cafile=ca
        )
        add(
            "HN-TLS-SOCKET-NEG-EXPIRED-001",
            exp_probe.get("ok") is False and exp_probe.get("loopback") is True,
            {"verify_with_ca": exp_probe},
        )

        port = rt.start_tls_server(certs["cert"], certs["key"])

        dns = rt.resolve_dns(
            "updates.gunnchos.local",
            poisoned={"updates.gunnchos.local": "198.51.100.66"},
        )
        add("HN-DNS-001", dns.get("reason") == "malicious_dns", dns)

        r1 = rt.request("https://updates.gunnchos.local/pkg", tls_status="untrusted_ca")
        add("HN-TLS-001", r1["reason"] == "untrusted_tls" and r1["credentials_sent"] is False, r1)
        r2 = rt.request("https://updates.gunnchos.local/pkg", tls_status="hostname_mismatch")
        add("HN-TLS-002", r2["reason"] == "hostname_mismatch" and r2["credentials_sent"] is False, r2)
        r3 = rt.request("https://updates.gunnchos.local/pkg", tls_status="expired_cert")
        add("HN-TLS-003", r3["reason"] == "expired_cert" and r3["credentials_sent"] is False, r3)

        r4 = rt.request("https://updates.gunnchos.local/pkg", captive_portal=True)
        add("HN-CAPTIVE-001", r4["reason"] == "captive_portal" and r4["credentials_sent"] is False, r4)
        r5 = rt.request("http://updates.gunnchos.local/pkg")
        add("HN-HTTP-001", r5["reason"] == "http_downgrade" and r5["credentials_sent"] is False, r5)
        r6 = rt.request("https://evil.example/phish")
        add("HN-CRED-001", r6["credentials_sent"] is False and r6["ok"] is False, r6)

        rt.set_link(False)
        r7 = rt.request("https://api.gunnchos.local/v1")
        rt.set_link(True)
        r8 = rt.request(
            "https://api.gunnchos.local/v1",
            resolved_ip=rt.trusted_dns["api.gunnchos.local"],
        )
        add(
            "HN-LINK-001",
            r7["reason"] == "link_down"
            and r7["credentials_sent"] is False
            and r8["ok"] is True
            and r8["credentials_sent"] is True,
            {"down": r7, "up": r8},
        )

        add(
            "HN-TLS-MATERIAL-001",
            certs["mismatch"].is_file()
            and certs["expired"].is_file()
            and certs["cert"].is_file()
            and certs["ca"].is_file(),
            {
                "mismatch_cert": str(certs["mismatch"]),
                "expired_cert": str(certs["expired"]),
                "valid_cert": str(certs["cert"]),
                "ca_cert": str(certs["ca"]),
                "valid_not_before": certs["valid_not_before"],
                "valid_not_after": certs["valid_not_after"],
                "expired_not_before": certs["expired_not_before"],
                "expired_not_after": certs["expired_not_after"],
            },
        )

        coupled = rt.couple_to_continuity_on_cellular_compromise()
        add(
            "HN-COUPLE-REL16-CONTINUITY-001",
            coupled["dns"].get("reason") == "malicious_dns"
            and coupled["continuity_selected"] == "wifi"
            and coupled["cellular_rel16_disabled"] is True
            and coupled["rm520n_five_ga_claimed"] is False,
            coupled,
        )

    finally:
        rt.stop_tls_server()

    all_pass = all(c["passed"] for c in cases) and len(cases) >= 10
    no_leak = all(
        (e.get("credentials_sent") is False) or ("evil" not in str(e.get("origin", "")))
        for e in rt.vault.sent_to
    )
    ok = all_pass and no_leak
    return {
        "schema": "gunnchos.net_sec_rc001.hostile_network_digital.v1",
        "ok": ok,
        "scope": "LOCAL_LOOPBACK_SOCKET_TLS_DNS_POLICY",
        "uncontrolled_external_attack": False,
        "evidence_level": EVIDENCE_LEVEL,
        "RF_WIFI": RF_WIFI_STATUS,
        "cases": cases,
        "credential_events": rt.vault.sent_to,
        "coupled_to": ["terrestrial_rel16", "service_continuity"],
        "claim_boundary": (
            "Local loopback socket/TLS/DNS/policy hostile-network testbed coupled to "
            "Rel-16 terrestrial + continuity failover. No uncontrolled external attack. "
            "RF/Wi-Fi E5/E8 EXTERNAL_PENDING."
        ),
        "token_candidate": "HOSTILE_NETWORK_DIGITAL",
    }
