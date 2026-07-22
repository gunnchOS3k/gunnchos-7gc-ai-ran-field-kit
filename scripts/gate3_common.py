"""Gate 3 shared helpers: privacy scan, hashing, evidence labels."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

EVIDENCE_PHYSICAL = "controlled_device_measurement"
EVIDENCE_SYNTHETIC = "synthetic"
EVIDENCE_OPEN = "open_data"
EVIDENCE_SIM = "source_validated_simulation"

PROHIBITED_ALIASES = {
    "latitude", "longitude", "lat", "lon", "lng", "gps", "raw_gps", "coordinates",
    "street_address", "address", "email", "e_mail", "phone", "phone_number",
    "student_id", "imei", "imsi", "serial", "serial_number", "device_serial",
    "mac", "mac_address", "bssid", "ssid", "wifi_ssid", "advertising_id",
    "aaid", "idfa", "persistent_device_id", "contact", "account_id",
}


def normalize_key(key: str) -> str:
    s = str(key).strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


VALUE_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b", re.I),
    re.compile(r"\b\d{15}\b"),
]


def recursive_privacy_scan(obj: Any, path: str = "$") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}"
            norm = normalize_key(key)
            if norm in PROHIBITED_ALIASES:
                findings.append({"path": child, "kind": "prohibited_key", "detail": norm})
            findings.extend(recursive_privacy_scan(value, child))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            findings.extend(recursive_privacy_scan(item, f"{path}[{i}]"))
    elif isinstance(obj, str):
        for pat in VALUE_PATTERNS:
            if pat.search(obj):
                findings.append({"path": path, "kind": "prohibited_value", "detail": obj[:64]})
                break
    return findings


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return path
