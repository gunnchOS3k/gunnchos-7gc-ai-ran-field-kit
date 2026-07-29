#!/usr/bin/env python3
"""Shared helpers for Gates 4–6 Oulu/NVIDIA orchestration."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPOS_ROOT = Path(os.environ.get("REPOS_ROOT", ROOT.parent))
LOCK_PATH = ROOT / "CROSS_REPO_VERSION_LOCK.json"
STATUS_PATH = ROOT / "GATES_4_6_MASTER_STATUS.md"
STATUS_JSON = ROOT / "orchestration" / "gates_4_6" / "status.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_rev(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def git_branch(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        env=merged,
    )
    result = {
        "cmd": cmd,
        "cwd": str(cwd) if cwd else None,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-4000:],
        "stderr_tail": (proc.stderr or "")[-4000:],
        "ok": proc.returncode == 0,
    }
    if check and proc.returncode != 0:
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def detect_cuda() -> dict[str, Any]:
    nvidia = shutil.which("nvidia-smi")
    nvcc = shutil.which("nvcc")
    cuda_available = False
    gpu_name = None
    try:
        import torch  # type: ignore

        cuda_available = bool(torch.cuda.is_available())
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
    except Exception:
        pass
    return {
        "nvidia_smi": nvidia is not None,
        "nvcc": nvcc is not None,
        "torch_cuda": cuda_available,
        "gpu_name": gpu_name,
        "status": "AVAILABLE" if (cuda_available or nvidia) else "BLOCKED_HARDWARE",
    }


def host_manifest() -> dict[str, Any]:
    return {
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version.split()[0],
        "cuda": detect_cuda(),
        "docker": shutil.which("docker") is not None,
        "captured_at": utc_now(),
    }


def load_lock() -> dict[str, Any]:
    if not LOCK_PATH.exists():
        return {"components": {}}
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def verify_lock(fail_on_mismatch: bool = True) -> dict[str, Any]:
    lock = load_lock()
    components = lock.get("components") or {}
    results = []
    failures: list[str] = []
    for name, meta in components.items():
        rel = meta.get("path") or name
        path = REPOS_ROOT / rel
        expected = meta.get("commit")
        required = bool(meta.get("required", True))
        actual = git_rev(path) if path.is_dir() else None
        match = (actual == expected) if expected else actual is not None
        entry = {
            "repository": name,
            "path": str(path),
            "required": required,
            "expected_commit": expected,
            "actual_commit": actual,
            "branch": git_branch(path) if path.is_dir() else None,
            "match": match,
            "present": path.is_dir(),
        }
        results.append(entry)
        if required and not match:
            failures.append(name)
    report = {
        "ok": not failures,
        "failures": failures,
        "components": results,
        "lock_path": str(LOCK_PATH),
        "repos_root": str(REPOS_ROOT),
        "checked_at": utc_now(),
    }
    if fail_on_mismatch and failures:
        raise SystemExit(f"CROSS_REPO_VERSION_LOCK mismatch: {failures}")
    return report


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def update_master_status(statuses: dict[str, str], notes: list[str] | None = None) -> None:
    lines = [
        "# Gates 4–6 Master Status",
        "",
        f"**Updated:** {utc_now()}",
        "",
        "Namespace: Oulu GENOME + NVIDIA Aerial evidence program.",
        "Does **not** alter legacy field-kit `GATE_4_PASS` / `GATE_5_PASS` scientific statuses.",
        "",
        "| Status key | Value |",
        "|---|---|",
    ]
    for k, v in statuses.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append("## Notes")
    for n in notes or []:
        lines.append(f"- {n}")
    lines.append("")
    lines.append("## Non-claims")
    lines.append("- `NO_ACCEPTANCE_GUARANTEE`")
    lines.append("- `NVIDIA_TENURE_REQUIREMENT_UNSATISFIED` unless external career evidence is attached")
    lines.append("")
    STATUS_PATH.write_text("\n".join(lines), encoding="utf-8")
    write_json(STATUS_JSON, {"updated": utc_now(), "statuses": statuses, "notes": notes or []})
