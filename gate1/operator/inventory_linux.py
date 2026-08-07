"""Linux inventory probes — never invent hardware."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gate1.operator.probe import run_cmd, which


def inventory_linux() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    uname = run_cmd(["uname", "-a"], timeout=5)
    items.append(
        {
            "item_id": "linux.uname",
            "category": "host",
            "label": "Linux uname",
            "presence": "PRESENT_CONFIRMED" if uname["ok"] else uname["status"],
            "evidence": {
                "tool": "uname",
                "stdout_excerpt": (uname["stdout"] or "")[:500],
            },
            "blocker_class": None,
        }
    )

    if which("lsusb"):
        usb = run_cmd(["lsusb"], timeout=10)
        out = usb["stdout"] or ""
        presence = "PRESENT_CONFIRMED" if usb["ok"] and out.strip() else ("MISSING" if usb["ok"] else usb["status"])
        items.append(
            {
                "item_id": "linux.lsusb",
                "category": "usb",
                "label": "lsusb devices",
                "presence": presence,
                "evidence": {"tool": "lsusb", "stdout_excerpt": out[:1500]},
                "blocker_class": None if presence == "PRESENT_CONFIRMED" else "REQUIRES_LOCAL_HARDWARE",
            }
        )
    else:
        items.append(
            {
                "item_id": "linux.lsusb",
                "category": "usb",
                "label": "lsusb devices",
                "presence": "TOOLCHAIN_MISSING",
                "evidence": {"tool": "lsusb", "detail": "not found"},
                "blocker_class": "REQUIRES_TOOLCHAIN",
            }
        )

    sys_class = Path("/sys/class/net")
    if sys_class.exists():
        ifaces = sorted(p.name for p in sys_class.iterdir())
        items.append(
            {
                "item_id": "linux.net_ifaces",
                "category": "network",
                "label": "sysfs network interfaces",
                "presence": "PRESENT_CONFIRMED" if ifaces else "MISSING",
                "evidence": {"tool": "sysfs", "interfaces": ifaces},
                "blocker_class": None,
            }
        )
    return items
