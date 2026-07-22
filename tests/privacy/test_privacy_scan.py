"""Privacy scanner tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from gate3_common import recursive_privacy_scan  # noqa: E402


def test_nested_email_and_imei():
    findings = recursive_privacy_scan({"a": {"Email": "a@b.c", "device": {"IMEI": "490154203237518"}}})
    assert any(f["kind"] == "prohibited_key" for f in findings)


def test_mac_value_pattern():
    findings = recursive_privacy_scan({"note": "peer aa:bb:cc:dd:ee:ff"})
    assert findings
