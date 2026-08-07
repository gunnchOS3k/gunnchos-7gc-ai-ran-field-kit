#!/usr/bin/env python3
"""Checkout locked sibling repositories at exact SHAs.

Never rewrites the lock. Never prints or records credentials.

Credential precedence per repository:
1. Per-repo read-only SSH deploy key via PORTFOLIO_SSH_KEY_<NORMALIZED_REPO>
2. Explicit PORTFOLIO_CHECKOUT_TOKEN (GitHub App / dedicated PAT from workflow)
3. PORTFOLIO_REPO_READ_TOKEN
4. GITHUB_TOKEN (public siblings only; never sufficient alone for private siblings)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "integration" / "repo-lock.json"

# Repos known to require non-GITHUB_TOKEN credentials when private.
# Public repos may still list an SSH secret; absence is fine when HTTPS works.
SSH_SECRET_PREFIX = "PORTFOLIO_SSH_KEY_"


def _normalize_repo_secret_suffix(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


def _ssh_secret_name(name: str) -> str:
    return f"{SSH_SECRET_PREFIX}{_normalize_repo_secret_suffix(name)}"


def _sanitize_url(url: str) -> str:
    url = url.replace("gunnchos3k", "gunnchOS3k").replace("Gunnchos3k", "gunnchOS3k")
    if "github.com" in url and not url.endswith(".git"):
        url = url + ".git"
    return url


def _https_to_ssh(url: str) -> str:
    parsed = urlparse(_sanitize_url(url))
    path = parsed.path.lstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return f"git@github.com:{path}.git"


def _authed_url(url: str, token: str | None) -> str:
    """Embed token for HTTPS GitHub clone without logging the result."""
    if not token:
        return url
    parsed = urlparse(url)
    if "github.com" not in parsed.netloc:
        return url
    netloc = f"x-access-token:{quote(token, safe='')}@{parsed.hostname}"
    return urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))


def _redact(text: str, token: str | None) -> str:
    if not token:
        return text
    return text.replace(token, "***REDACTED***")


def _git(
    args: list[str],
    *,
    cwd: Path | None = None,
    token: str | None = None,
    env_extra: dict[str, str] | None = None,
) -> str:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    if env_extra:
        env.update(env_extra)
    try:
        return subprocess.check_output(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            stderr=subprocess.STDOUT,
            env=env,
        ).strip()
    except subprocess.CalledProcessError as exc:
        out = _redact(exc.output or "", token)
        raise RuntimeError(f"git failed ({exc.returncode}): {out}") from None


def _detect_https_credential() -> tuple[str | None, str]:
    if os.environ.get("PORTFOLIO_CHECKOUT_TOKEN"):
        src = os.environ.get("PORTFOLIO_CREDENTIAL_SOURCE") or "github_app"
        return os.environ["PORTFOLIO_CHECKOUT_TOKEN"], src
    if os.environ.get("PORTFOLIO_REPO_READ_TOKEN"):
        return os.environ["PORTFOLIO_REPO_READ_TOKEN"], "pat"
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"], "github_token"
    return None, "none"


def _resolve_ssh_key_material(name: str) -> tuple[str | None, str]:
    """Return (key_pem_or_path_hint, source_label).

    Accepts either:
    - PORTFOLIO_SSH_KEY_<REPO>=PEM contents
    - PORTFOLIO_SSH_KEY_<REPO>_FILE=/path/to/key
    - PORTFOLIO_SSH_KEY_DIR/<repo> file
    """
    secret = _ssh_secret_name(name)
    file_env = f"{secret}_FILE"
    if os.environ.get(file_env):
        return os.environ[file_env], "deploy_key_file"
    if os.environ.get(secret):
        return os.environ[secret], "deploy_key_env"
    key_dir = os.environ.get("PORTFOLIO_SSH_KEY_DIR")
    if key_dir:
        candidate = Path(key_dir) / name
        if candidate.is_file():
            return str(candidate), "deploy_key_dir"
    return None, "none"


def _ssh_env_for_key(material: str, source: str) -> tuple[dict[str, str], Callable[[], None]]:
    """Build GIT_SSH_COMMAND env and a cleanup callback. Never logs key bytes."""
    tmp_path: Path | None = None
    if source == "deploy_key_env":
        fd, path = tempfile.mkstemp(prefix="portfolio-ssh-", suffix=".key")
        os.close(fd)
        tmp_path = Path(path)
        os.chmod(tmp_path, 0o600)
        # Normalize newlines; secrets may arrive with escaped newlines from YAML
        pem = material.replace("\\n", "\n")
        if not pem.endswith("\n"):
            pem += "\n"
        tmp_path.write_text(pem, encoding="utf-8")
        key_path = tmp_path
    else:
        key_path = Path(material)
        os.chmod(key_path, 0o600)

    ssh_cmd = (
        f"ssh -i {key_path} -o IdentitiesOnly=yes "
        f"-o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/tmp/portfolio_known_hosts"
    )
    env = {"GIT_SSH_COMMAND": ssh_cmd, "GIT_SSH_VARIANT": "ssh"}

    def cleanup() -> None:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    return env, cleanup


def checkout_one(
    name: str,
    meta: dict,
    repos_root: Path,
    https_token: str | None,
    https_credential_source: str,
) -> dict:
    rel = meta.get("local_path_hint") or meta.get("path") or name
    commit = meta.get("commit") or ""
    required = bool(meta.get("required", True))
    url = _sanitize_url(
        meta.get("repository_url") or meta.get("repository") or f"https://github.com/gunnchOS3k/{name}"
    )
    dest = repos_root / rel
    ssh_material, ssh_source = _resolve_ssh_key_material(name)
    use_ssh = ssh_material is not None and ssh_source != "none"
    credential_source = ssh_source if use_ssh else https_credential_source
    entry = {
        "repository": name,
        "required": required,
        "expected_commit": commit,
        "actual_commit": None,
        "checkout_status": "pending",
        "credential_source": credential_source,
        "transport": "ssh" if use_ssh else "https",
        "token_exposed": False,
        "error_class": None,
        "path": str(dest),
    }
    if not commit or commit == "0" * 40:
        entry["checkout_status"] = "failed"
        entry["error_class"] = "empty_commit"
        return entry

    cleanup = lambda: None  # noqa: E731
    try:
        if use_ssh:
            env_extra, cleanup = _ssh_env_for_key(ssh_material, ssh_source)
            clone_url = _https_to_ssh(url)
            fetch_url = clone_url
            token_for_redact = None
        else:
            env_extra = {}
            clone_url = _authed_url(url, https_token)
            fetch_url = clone_url
            token_for_redact = https_token

        if not dest.exists():
            _git(
                ["git", "clone", "--no-checkout", clone_url, str(dest)],
                token=token_for_redact,
                env_extra=env_extra,
            )
            _git(
                ["git", "-C", str(dest), "remote", "set-url", "origin", url if not use_ssh else clone_url],
                token=token_for_redact,
                env_extra=env_extra,
            )
        try:
            _git(
                ["git", "-C", str(dest), "fetch", "--depth", "1", fetch_url, commit],
                token=token_for_redact,
                env_extra=env_extra,
            )
        except RuntimeError:
            _git(
                ["git", "-C", str(dest), "remote", "set-url", "origin", fetch_url],
                token=token_for_redact,
                env_extra=env_extra,
            )
            _git(
                ["git", "-C", str(dest), "fetch", "--depth", "1", "origin", commit],
                token=token_for_redact,
                env_extra=env_extra,
            )
            _git(
                [
                    "git",
                    "-C",
                    str(dest),
                    "remote",
                    "set-url",
                    "origin",
                    url if not use_ssh else clone_url,
                ],
                token=token_for_redact,
                env_extra=env_extra,
            )
        _git(["git", "-C", str(dest), "checkout", "--force", commit], token=token_for_redact, env_extra=env_extra)
        _git(["git", "-C", str(dest), "reset", "--hard", commit], token=token_for_redact, env_extra=env_extra)
        _git(["git", "-C", str(dest), "clean", "-fd"], token=token_for_redact, env_extra=env_extra)
        actual = _git(["git", "-C", str(dest), "rev-parse", "HEAD"], token=token_for_redact, env_extra=env_extra)
        entry["actual_commit"] = actual
        if actual != commit:
            entry["checkout_status"] = "failed"
            entry["error_class"] = "commit_mismatch"
        else:
            entry["checkout_status"] = "ok"
    except Exception as exc:
        msg = _redact(str(exc), https_token)
        entry["checkout_status"] = "failed"
        if (
            "Authentication" in msg
            or "could not read Username" in msg
            or "Permission denied" in msg
            or "128" in msg
            or "Repository not found" in msg
        ):
            if credential_source == "none":
                entry["error_class"] = "BLOCKED_CREDENTIAL_CONFIGURATION"
            else:
                entry["error_class"] = "auth_or_access_denied"
        elif "not found" in msg.lower():
            entry["error_class"] = "missing_repository"
        else:
            entry["error_class"] = "checkout_error"
        entry["error_detail"] = msg[:500]
    finally:
        cleanup()

    blob = json.dumps(entry)
    if https_token and https_token in blob:
        entry = {k: ("***" if isinstance(v, str) and https_token in v else v) for k, v in entry.items()}
        entry["token_exposed"] = False
        entry["error_class"] = entry.get("error_class") or "token_sanitization"
    return entry


def _private_repos_need_credentials(lock: dict) -> list[str]:
    """Repos that historically require non-default GITHUB_TOKEN when private."""
    needed = []
    for name, meta in (lock.get("components") or {}).items():
        if meta.get("self_pin_policy") == "workflow_checked_commit":
            continue
        if name == "gunnchos-7gc-ai-ran-field-kit":
            continue
        # Prefer explicit visibility; treat unknown as may-need-cred if required.
        vis = (meta.get("visibility") or "").lower()
        if vis == "public":
            continue
        # If a deploy-key secret is configured, this repo is covered.
        mat, src = _resolve_ssh_key_material(name)
        if mat and src != "none":
            continue
        needed.append(name)
    return needed


def checkout_all(lock_path: Path, repos_root: Path) -> dict:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    https_token, https_credential_source = _detect_https_credential()
    components = []
    failures = []
    blocked_credentials = False
    ssh_repos = []
    for name, meta in (lock.get("components") or {}).items():
        if meta.get("self_pin_policy") == "workflow_checked_commit":
            continue
        if name == "gunnchos-7gc-ai-ran-field-kit":
            continue
        entry = checkout_one(name, meta, repos_root, https_token, https_credential_source)
        components.append(entry)
        if entry.get("transport") == "ssh" and entry["checkout_status"] == "ok":
            ssh_repos.append(name)
        if entry["checkout_status"] != "ok":
            if entry.get("required", True):
                failures.append(entry["repository"])
                if entry.get("error_class") == "BLOCKED_CREDENTIAL_CONFIGURATION":
                    blocked_credentials = True

    # If HTTPS has no token but every required private sibling has a deploy key
    # path available, do not treat missing App/PAT as a hard block up-front.
    uncovered = _private_repos_need_credentials(lock)
    if https_credential_source == "none" and uncovered and not any(
        c.get("transport") == "ssh" for c in components
    ):
        # No HTTPS token and no SSH material used — still blocked.
        blocked_credentials = True

    report = {
        "ok": not failures,
        "repos_root": str(repos_root),
        "lock_path": str(lock_path),
        "credential_source": (
            "deploy_key+https_fallback"
            if ssh_repos and https_token
            else ("deploy_key" if ssh_repos else https_credential_source)
        ),
        "ssh_deploy_key_repos": ssh_repos,
        "token_exposed": False,
        "blocked_credential_configuration": blocked_credentials,
        "failures": failures,
        "components": components,
        "status": (
            "BLOCKED_CREDENTIAL_CONFIGURATION"
            if blocked_credentials
            else ("CHECKOUT_PASS" if not failures else "CHECKOUT_FAIL")
        ),
        "portfolio_cross_repo_read_access": (
            "PORTFOLIO_CROSS_REPO_READ_ACCESS_PASS"
            if not failures and not blocked_credentials
            else "PORTFOLIO_CROSS_REPO_READ_ACCESS_FAIL"
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
    token = (
        os.environ.get("PORTFOLIO_CHECKOUT_TOKEN")
        or os.environ.get("PORTFOLIO_REPO_READ_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
    )
    text = _redact(text, token)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    if report.get("blocked_credential_configuration"):
        return 3
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
