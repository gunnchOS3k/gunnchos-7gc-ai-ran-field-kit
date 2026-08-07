"""Android / ADB inventory — never invent devices."""

from __future__ import annotations

from typing import Any

from gate1.operator.probe import run_cmd, which


def inventory_android() -> list[dict[str, Any]]:
    if not which("adb"):
        return [
            {
                "item_id": "android.adb",
                "category": "android",
                "label": "Android Debug Bridge",
                "presence": "TOOLCHAIN_MISSING",
                "evidence": {"tool": "adb", "detail": "adb not on PATH"},
                "blocker_class": "REQUIRES_TOOLCHAIN",
            }
        ]

    res = run_cmd(["adb", "devices", "-l"], timeout=15)
    if res["status"] == "TOOLCHAIN_MISSING":
        presence = "TOOLCHAIN_MISSING"
        devices: list[str] = []
    else:
        lines = [
            ln.strip()
            for ln in (res["stdout"] or "").splitlines()
            if ln.strip() and not ln.startswith("List of devices")
        ]
        devices = [ln for ln in lines if "device" in ln.split() or "unauthorized" in ln or "offline" in ln]
        if any(ln.split()[1] == "device" for ln in devices if len(ln.split()) >= 2):
            presence = "PRESENT_CONFIRMED"
        elif devices:
            presence = "INDETERMINATE"
        else:
            presence = "MISSING"

    return [
        {
            "item_id": "android.adb_devices",
            "category": "android",
            "label": "ADB connected devices",
            "presence": presence,
            "evidence": {
                "tool": "adb",
                "argv": res["argv"],
                "returncode": res["returncode"],
                "device_lines": devices,
                "stdout_excerpt": (res["stdout"] or "")[:1500],
                "stderr_excerpt": (res["stderr"] or "")[:400],
            },
            "blocker_class": None if presence == "PRESENT_CONFIRMED" else "REQUIRES_LOCAL_HARDWARE",
        }
    ]
