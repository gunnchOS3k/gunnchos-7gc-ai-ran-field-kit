#!/usr/bin/env python3
"""Checkout locked sibling repositories at exact SHAs.

Never rewrites the lock. Never prints or records credentials.
Credential is read only from PORTFOLIO_CHECKOUT_TOKEN / GITHUB_TOKEN env.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "integration" / "repo-lock.json"


def _sanitize_url(url: str) -> str:
    url = url.replace("gunnchos3k", "gunnchOS3k").replace("Gunnchos3k", "gunnchOS3k")
    if "github.com" in url and not url.endswith(".git"):
        url = url + ".git"
    return url


def _authed_url(url: str, token: str | None) -> str:
    """Embed token for HTTPS GitHub clone without logging the result."""
    if not token:
        return url
    parsed = urlparse(url)
    if "github.com" not in parsed.netloc:
        return url
    # x-access-token:TOKEN@host — never return this string to logs/reports
    netloc = f"x-access-token:{quote(token, safe='')}@{parsed.hostname}"
    return urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))


def _redact(text: str, token: str | None) -> str:
    if not token:
        return text
    return text.replace(token, "***REDACTED***")


def _git(args: list[str], *, cwd: Path | None = None, token: str | None = None) -> str:
    env = os.environ.copy()
    # Prevent interactive credential prompts in CI
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    try:
        return subprocess.check_output(args, cwd=str(cwd) if cwd else None, text=True, stderr=subprocess.STDOUT, env=env).strip()
    except subprocess.CalledProcessError as exc:
        out = _redact(exc.output or "", token)
        raise RuntimeError(f"git failed ({exc.returncode}): {out}") from None


def _detect_credential_source() -> tuple[str | None, str]:
    if os.environ.get("PORTFOLIO_CHECKOUT_TOKEN"):
        # Prefer explicitly minted App / PAT token from workflow
        src = os.environ.get("PORTFOLIO_CREDENTIAL_SOURCE") or "github_app"
        return os.environ["PORTFOLIO_CHECKOUT_TOKEN"], src
    if os.environ.get("PORTFOLIO_REPO_READ_TOKEN"):
        return os.environ["PORTFOLIO_REPO_READ_TOKEN"], "pat"
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"], "github_token"
    return None, "none"


def checkout_one(
    name: str,
    meta: dict,
    repos_root: Path,
    token: str | None,
    credential_source: str,
) -> dict:
    rel = meta.get("local_path_hint") or meta.get("path") or name
    commit = meta.get("commit") or ""
    required = bool(meta.get("required", True))
    url = _sanitize_url(meta.get("repository_url") or meta.get("repository") or f"https://github.com/gunnchOS3k/{name}")
    dest = repos_root / rel
    entry = {
        "repository": name,
        "required": required,
        "expected_commit": commit,
        "actual_commit": None,
        "checkout_status": "pending",
        "credential_source": credential_source,
        "token_exposed": False,
        "error_class": None,
        "path": str(dest),
    }
    if not commit or commit == "0" * 40:
        entry["checkout_status"] = "failed"
        entry["error_class"] = "empty_commit"
        return entry
    try:
        clone_url = _authed_url(url, token)
        if not dest.exists():
            # Use GIT_ASKPASS-free URL; never print clone_url
            _git(["git", "clone", "--no-checkout", clone_url, str(dest)], token=token)
            # Rewrite remote to tokenless URL for subsequent local use
            _git(["git", "-C", str(dest), "remote", "set-url", "origin", url], token=token)
        # Fetch exact SHA without relying on branch tip
        fetch_url = _authed_url(url, token)
        try:
            _git(["git", "-C", str(dest), "fetch", "--depth", "1", fetch_url, commit], token=token)
        except RuntimeError:
            # Some hosts need origin + ref; retry with origin if configured
            _git(["git", "-C", str(dest), "remote", "set-url", "origin", fetch_url], token=token)
            _git(["git", "-C", str(dest), "fetch", "--depth", "1", "origin", commit], token=token)
            _git(["git", "-C", str(dest), "remote", "set-url", "origin", url], token=token)
        _git(["git", "-C", str(dest), "checkout", "--force", commit], token=token)
        _git(["git", "-C", str(dest), "reset", "--hard", commit], token=token)
        _git(["git", "-C", str(dest), "clean", "-fd"], token=token)
        actual = _git(["git", "-C", str(dest), "rev-parse", "HEAD"], token=token)
        entry["actual_commit"] = actual
        if actual != commit:
            entry["checkout_status"] = "failed"
            entry["error_class"] = "commit_mismatch"
        else:
            entry["checkout_status"] = "ok"
    except Exception as exc:
        msg = _redact(str(exc), token)
        entry["checkout_status"] = "failed"
        if "Authentication" in msg or "could not read Username" in msg or "128" in msg or "Repository not found" in msg:
            if credential_source == "none":
                entry["error_class"] = "BLOCKED_CREDENTIAL_CONFIGURATION"
            else:
                entry["error_class"] = "auth_or_access_denied"
        elif "not found" in msg.lower():
            entry["error_class"] = "missing_repository"
        else:
            entry["error_class"] = "checkout_error"
        entry["error_detail"] = msg[:500]
    # Safety: ensure token never appears in serialized entry
    blob = json.dumps(entry)
    if token and token in blob:
        entry = {k: ("***" if isinstance(v, str) and token in v else v) for k, v in entry.items()}
        entry["token_exposed"] = False
        entry["error_class"] = entry.get("error_class") or "token_sanitization"
    return entry


def checkout_all(lock_path: Path, repos_root: Path) -> dict:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    token, credential_source = _detect_credential_source()
    components = []
    failures = []
    blocked_credentials = False
    for name, meta in (lock.get("components") or {}).items():
        # Control-plane self entry must not appear as a sibling pin.
        if meta.get("self_pin_policy") == "workflow_checked_commit":
            continue
        if name == "gunnchos-7gc-ai-ran-field-kit":
            continue
        entry = checkout_one(name, meta, repos_root, token, credential_source)
        components.append(entry)
        if entry["checkout_status"] != "ok":
            if entry.get("required", True):
                failures.append(entry["repository"])
                if entry.get("error_class") == "BLOCKED_CREDENTIAL_CONFIGURATION":
                    blocked_credentials = True
    report = {
        "ok": not failures,
        "repos_root": str(repos_root),
        "lock_path": str(lock_path),
        "credential_source": credential_source,
        "token_exposed": False,
        "blocked_credential_configuration": blocked_credentials,
        "failures": failures,
        "components": components,
        "status": (
            "BLOCKED_CREDENTIAL_CONFIGURATION"
            if blocked_credentials
            else ("CHECKOUT_PASS" if not failures else "CHECKOUT_FAIL")
        ),
    }
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lock", default=str(DEFAULT_LOCK))
    p.add_argument("--repos-root", default=str(ROOT.parent))
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)
    report = checkout_all(Path(args.lock), Path(args.repos_root))
    text = json.dumps(report, indent=2) + "\n"
    # Final redact pass
    token = os.environ.get("PORTFOLIO_CHECKOUT_TOKEN") or os.environ.get("PORTFOLIO_REPO_READ_TOKEN") or os.environ.get("GITHUB_TOKEN")
    text = _redact(text, token)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    if report.get("blocked_credential_configuration"):
        return 3
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
