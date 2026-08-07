"""USB inventory cross-platform facade."""

from __future__ import annotations

import platform
from typing import Any

from gate1.operator.inventory_linux import inventory_linux
from gate1.operator.inventory_macos import inventory_macos
from gate1.operator.probe import run_cmd, which


def inventory_usb() -> list[dict[str, Any]]:
    system = platform.system().lower()
    if system == "darwin":
        # Prefer macOS USB section from system_profiler already covered; add ioreg USB hint
        if which("ioreg"):
            res = run_cmd(["ioreg", "-p", "IOUSB", "-w", "0"], timeout=15)
            out = res["stdout"] or ""
            if res["status"] == "TOOLCHAIN_MISSING":
                presence = "TOOLCHAIN_MISSING"
            elif res["ok"] and ("USB" in out or "IOUSB" in out or out.strip()):
                # Presence of USB tree ≠ presence of Gate 1 prototypes
                presence = "PRESENT_CONFIRMED" if "Vendor" in out or "Product" in out or "IOUSBHostDevice" in out else "MISSING"
            else:
                presence = "INDETERMINATE"
            return [
                {
                    "item_id": "usb.ioreg",
                    "category": "usb",
                    "label": "IOUSB registry",
                    "presence": presence,
                    "evidence": {
                        "tool": "ioreg",
                        "argv": res["argv"],
                        "stdout_excerpt": out[:2000],
                        "note": "USB bus observation only; does not confirm ring/dock prototypes",
                    },
                    "blocker_class": None if presence == "PRESENT_CONFIRMED" else "REQUIRES_LOCAL_HARDWARE",
                }
            ]
        return inventory_macos()
    if system == "linux":
        return [i for i in inventory_linux() if i.get("category") == "usb"]
    return [
        {
            "item_id": "usb.unsupported",
            "category": "usb",
            "label": "USB inventory",
            "presence": "UNSUPPORTED_PLATFORM",
            "evidence": {"platform": platform.system()},
            "blocker_class": "REQUIRES_SUPPORTED_HOST",
        }
    ]
