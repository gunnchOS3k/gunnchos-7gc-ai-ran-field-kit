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


def test_pixel_calibration_run_id_not_flagged_as_phone():
    from validate_contract import find_prohibited_identifiers

    batch = {
        "run_id": "pixel-cal-1784756973874",
        "site_id": "gary",
        "note": "ok",
    }
    assert find_prohibited_identifiers(batch) == []


def test_real_phone_still_flagged():
    from validate_contract import find_prohibited_identifiers

    findings = find_prohibited_identifiers({"operator_note": "call 312-555-0199"})
    assert findings
