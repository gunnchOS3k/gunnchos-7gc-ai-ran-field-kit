"""Safe subprocess helpers for inventory probes — never invent hardware."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def run_cmd(argv: list[str], *, timeout: float = 20.0) -> dict[str, Any]:
    """Run a command; capture stdout/stderr; never raise for missing tools."""
    exe = argv[0] if argv else ""
    if not which(exe):
        return {
            "ok": False,
            "status": "TOOLCHAIN_MISSING",
            "argv": argv,
            "stdout": "",
            "stderr": f"executable not found: {exe}",
            "returncode": None,
        }
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except PermissionError as exc:
        return {
            "ok": False,
            "status": "PERMISSION_DENIED",
            "argv": argv,
            "stdout": "",
            "stderr": str(exc),
            "returncode": None,
        }
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or b""
        err = exc.stderr or b""
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": "INDETERMINATE",
            "argv": argv,
            "stdout": out,
            "stderr": f"timeout after {timeout}s; {err}",
            "returncode": None,
        }
    except OSError as exc:
        return {
            "ok": False,
            "status": "INDETERMINATE",
            "argv": argv,
            "stdout": "",
            "stderr": str(exc),
            "returncode": None,
        }
    stdout = (proc.stdout or b"").decode("utf-8", errors="replace")
    stderr = (proc.stderr or b"").decode("utf-8", errors="replace")
    return {
        "ok": proc.returncode == 0,
        "status": "OK" if proc.returncode == 0 else "INDETERMINATE",
        "argv": argv,
        "stdout": stdout,
        "stderr": stderr,
        "returncode": proc.returncode,
    }
