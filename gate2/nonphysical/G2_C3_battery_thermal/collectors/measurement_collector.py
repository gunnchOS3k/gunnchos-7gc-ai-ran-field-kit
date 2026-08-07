"""Physical measurement collector stub — REAL_MEASUREMENT_PENDING."""
from __future__ import annotations

STATUS = "REAL_MEASUREMENT_PENDING"
SYSTEM_TOKEN = "BATTERY_THERMAL_NONPHYSICAL_SYSTEM_COMPLETE"

def collector_status() -> dict:
    return {
        "system_token": SYSTEM_TOKEN,
        "measurement_token": STATUS,
        "evidence_class_allowed_now": ["MODELED", "SIMULATED"],
        "evidence_class_pending": ["MEASURED"],
        "samples": [],
    }
