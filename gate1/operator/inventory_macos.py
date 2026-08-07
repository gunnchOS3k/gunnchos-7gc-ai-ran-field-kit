"""macOS inventory probes via system_profiler / ioreg / pmset / networksetup / ifconfig."""

from __future__ import annotations

from typing import Any

from gate1.operator.probe import run_cmd, which


def inventory_macos() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not which("system_profiler"):
        return [
            {
                "item_id": "macos.host",
                "category": "host",
                "label": "macOS host profile",
                "presence": "TOOLCHAIN_MISSING",
                "evidence": {"tool": "system_profiler", "detail": "not found"},
                "blocker_class": "REQUIRES_TOOLCHAIN",
            }
        ]

    hw = run_cmd(["system_profiler", "SPHardwareDataType", "-json"], timeout=30)
    if hw["status"] == "TOOLCHAIN_MISSING":
        presence = "TOOLCHAIN_MISSING"
    elif hw["ok"] and hw["stdout"].strip():
        presence = "PRESENT_CONFIRMED"
    elif hw["status"] == "PERMISSION_DENIED":
        presence = "PERMISSION_DENIED"
    else:
        presence = "INDETERMINATE"
    items.append(
        {
            "item_id": "macos.host_hardware",
            "category": "host",
            "label": "macOS SPHardwareDataType",
            "presence": presence,
            "evidence": {
                "tool": "system_profiler",
                "argv": hw["argv"],
                "returncode": hw["returncode"],
                "stdout_excerpt": (hw["stdout"] or "")[:2000],
                "stderr_excerpt": (hw["stderr"] or "")[:500],
            },
            "blocker_class": None if presence == "PRESENT_CONFIRMED" else "REQUIRES_LOCAL_HARDWARE",
        }
    )

    usb = run_cmd(["system_profiler", "SPUSBDataType", "-json"], timeout=30)
    usb_out = usb["stdout"] or ""
    usb_presence = (
        "PRESENT_CONFIRMED"
        if usb["ok"] and ("Vendor" in usb_out or "Product" in usb_out or "usb" in usb_out.lower())
        else ("TOOLCHAIN_MISSING" if usb["status"] == "TOOLCHAIN_MISSING" else "MISSING")
    )
    # Empty USB bus can be valid — treat successful empty profile as MISSING devices
    if usb["ok"] and not ("Vendor" in usb_out or "Product" in usb_out):
        usb_presence = "MISSING"
    items.append(
        {
            "item_id": "macos.usb_bus",
            "category": "usb",
            "label": "macOS USB device bus",
            "presence": usb_presence,
            "evidence": {
                "tool": "system_profiler",
                "argv": usb["argv"],
                "returncode": usb["returncode"],
                "stdout_excerpt": usb_out[:2000],
            },
            "blocker_class": None if usb_presence == "PRESENT_CONFIRMED" else "REQUIRES_LOCAL_HARDWARE",
        }
    )

    for tool, item_id, label, category in [
        ("ioreg", "macos.ioreg", "IOKit registry probe", "host"),
        ("pmset", "macos.power", "Power management probe", "power"),
        ("networksetup", "macos.networksetup", "Network setup probe", "network"),
        ("ifconfig", "macos.ifconfig", "Network interfaces", "network"),
    ]:
        if tool == "ioreg":
            # Avoid full -l dump (binary noise / huge); class listing is enough for presence.
            res = run_cmd(["ioreg", "-c", "IOPlatformExpertDevice", "-d", "1"], timeout=15)
        elif tool == "pmset":
            res = run_cmd(["pmset", "-g"], timeout=10)
        elif tool == "networksetup":
            res = run_cmd(["networksetup", "-listallhardwareports"], timeout=10)
        else:
            res = run_cmd(["ifconfig"], timeout=10)
        if res["status"] == "TOOLCHAIN_MISSING":
            presence = "TOOLCHAIN_MISSING"
        elif res["ok"] and (res["stdout"] or "").strip():
            presence = "PRESENT_CONFIRMED"
        elif res["status"] == "PERMISSION_DENIED":
            presence = "PERMISSION_DENIED"
        else:
            presence = "INDETERMINATE"
        items.append(
            {
                "item_id": item_id,
                "category": category,
                "label": label,
                "presence": presence,
                "evidence": {
                    "tool": tool,
                    "argv": res["argv"],
                    "returncode": res["returncode"],
                    "stdout_excerpt": (res["stdout"] or "")[:1500],
                    "stderr_excerpt": (res["stderr"] or "")[:400],
                },
                "blocker_class": None if presence == "PRESENT_CONFIRMED" else "REQUIRES_TOOLCHAIN",
            }
        )
    return items
