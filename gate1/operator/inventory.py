"""Aggregate host inventory without inventing hardware."""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from typing import Any

from gate1.operator.inventory_android import inventory_android
from gate1.operator.inventory_linux import inventory_linux
from gate1.operator.inventory_macos import inventory_macos
from gate1.operator.inventory_usb import inventory_usb

# Gate 1 physical capability targets — never assume PRESENT
REQUIRED_CAPABILITIES = [
    {
        "capability_id": "representative_boot_hardware",
        "workstream": "boot",
        "default_presence": "MISSING_ASSUMED",
        "blocker_class": "REQUIRES_LOCAL_HARDWARE",
    },
    {
        "capability_id": "ring_prototype",
        "workstream": "ring-auth",
        "default_presence": "MISSING_ASSUMED",
        "blocker_class": "REQUIRES_PHYSICAL_PROTOTYPE",
    },
    {
        "capability_id": "dock_station",
        "workstream": "dock",
        "default_presence": "MISSING_ASSUMED",
        "blocker_class": "REQUIRES_PHYSICAL_PROTOTYPE",
    },
    {
        "capability_id": "on_device_ai_runtime_target",
        "workstream": "ai-runtime",
        "default_presence": "MISSING_ASSUMED",
        "blocker_class": "REQUIRES_LOCAL_HARDWARE",
    },
    {
        "capability_id": "game_target_device",
        "workstream": "games",
        "default_presence": "MISSING_ASSUMED",
        "blocker_class": "REQUIRES_LOCAL_HARDWARE",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_inventory() -> dict[str, Any]:
    system = platform.system().lower()
    observed: list[dict[str, Any]] = []
    if system == "darwin":
        observed.extend(inventory_macos())
        observed.extend(inventory_usb())
        observed.extend(inventory_android())
    elif system == "linux":
        observed.extend(inventory_linux())
        observed.extend(inventory_usb())
        observed.extend(inventory_android())
    else:
        observed.append(
            {
                "item_id": "host.unsupported",
                "category": "host",
                "label": f"Unsupported host OS: {platform.system()}",
                "presence": "UNSUPPORTED_PLATFORM",
                "evidence": {"platform": platform.platform()},
                "blocker_class": "REQUIRES_SUPPORTED_HOST",
            }
        )

    # Map required Gate 1 capabilities — never auto-upgrade to PRESENT_CONFIRMED
    # unless operator explicitly correlates an observed device (not done here).
    capabilities = []
    android_present = any(
        i.get("item_id") == "android.adb_devices" and i.get("presence") == "PRESENT_CONFIRMED"
        for i in observed
    )
    for cap in REQUIRED_CAPABILITIES:
        presence = cap["default_presence"]
        note = "No automatic correlation from host probes to Gate 1 prototypes."
        # Only soft hint: an ADB device PRESENT does not prove it is the Gate 1 target
        if android_present and cap["capability_id"] in {
            "representative_boot_hardware",
            "on_device_ai_runtime_target",
            "game_target_device",
        }:
            presence = "INDETERMINATE"
            note = (
                "ADB reports at least one device; operator must confirm it is the Gate 1 target. "
                "Not auto-labeled PRESENT_CONFIRMED."
            )
        capabilities.append(
            {
                "item_id": f"capability.{cap['capability_id']}",
                "category": "gate1_capability",
                "label": cap["capability_id"],
                "workstream": cap["workstream"],
                "presence": presence,
                "evidence": {"note": note},
                "blocker_class": cap["blocker_class"],
            }
        )

    return {
        "schema_version": "1.0.0",
        "collected_at_utc": utc_now(),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "assumption": "Equipment existence is NEVER assumed. PRESENT_CONFIRMED requires observation.",
        "observed_items": observed,
        "gate1_capabilities": capabilities,
        "summary": {
            "observed_count": len(observed),
            "present_confirmed": sum(1 for i in observed if i.get("presence") == "PRESENT_CONFIRMED"),
            "missing": sum(1 for i in observed if i.get("presence") == "MISSING"),
            "toolchain_missing": sum(1 for i in observed if i.get("presence") == "TOOLCHAIN_MISSING"),
            "capabilities_present_confirmed": sum(
                1 for i in capabilities if i.get("presence") == "PRESENT_CONFIRMED"
            ),
        },
    }
