#!/usr/bin/env python3
"""Generate contract-valid seven-campus fixtures and invalid counterparts."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from control_plane.closed_loop import git_commit, run_seven_campus_loop, sha256_obj  # noqa: E402


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def reason(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> int:
    commit = git_commit(ROOT)
    commits = {
        "field_kit": commit,
        "digital_twin": commit,
        "spectrumx": commit,
        "edge_io": commit,
    }
    bundle = run_seven_campus_loop(commits=commits)
    out_dir = ROOT / "fixtures" / "closed_loop_v2"
    valid = ROOT / "fixtures" / "valid"
    for result in bundle["results"]:
        site = result["site_id"]
        write(out_dir / f"{site}.design.json", result["design"])
        write(out_dir / f"{site}.twin.json", result["twin"])
        write(out_dir / f"{site}.optimization.json", result["optimization"])
        write(out_dir / f"{site}.mapping.json", result["mapping"])
        write(out_dir / f"{site}.calibration.json", result["calibration"])
        write(out_dir / f"{site}.actuation_request.json", result["actuation_request"])
        write(out_dir / f"{site}.actuation_receipt.json", result["actuation_receipt"])
        write(out_dir / f"{site}.hashes.json", result["hashes"])

    gary = next(r for r in bundle["results"] if r["site_id"] == "gary")
    write(valid / "campus_design_bundle.valid.json", gary["design"])
    write(valid / "campus_optimization_result.valid.json", gary["optimization"])
    write(valid / "twin_calibration_bundle.valid.json", gary["calibration"])
    write(valid / "ran_actuation_request.valid.json", gary["actuation_request"])
    write(valid / "ran_actuation_receipt.valid.json", gary["actuation_receipt"])
    write(valid / "campus_measurement_mapping.valid.json", gary["mapping"])

    # Invalid campus design family
    inv = ROOT / "fixtures" / "invalid" / "campus"
    bad = deepcopy(gary["design"])
    del bad["campus_slug"]
    write(inv / "missing_campus_slug.json", bad)
    reason(inv / "missing_campus_slug.reason.txt", "campus_slug is required for MLV V2 compatibility")

    bad = deepcopy(gary["design"])
    bad["source_manifest_sha256"] = "deadbeef"
    write(inv / "bad_source_hash.json", bad)
    reason(inv / "bad_source_hash.reason.txt", "source_manifest_sha256 must be 64 hex chars")

    bad = deepcopy(gary["design"])
    bad["schema_version"] = "2.0.0"
    write(inv / "unsupported_major.json", bad)
    reason(inv / "unsupported_major.reason.txt", "major version 2 is unsupported")

    bad = deepcopy(gary["design"])
    bad["privacy"]["contains_person_path"] = True
    write(inv / "person_path.json", bad)
    reason(inv / "person_path.reason.txt", "person-path tracking is forbidden")

    bad = deepcopy(gary["design"])
    bad["site_id"] = "gaza"
    bad["campus_slug"] = "gaza"
    bad["privacy"]["gaza_sensitive_export"] = True
    write(inv / "gaza_sensitive_export.json", bad)
    reason(inv / "gaza_sensitive_export.reason.txt", "Gaza sensitive export must stay false")

    # Invalid optimization
    inv = ROOT / "fixtures" / "invalid" / "optimization"
    bad = deepcopy(gary["optimization"])
    bad["alternatives"] = bad["alternatives"][:1]
    write(inv / "single_alternative.json", bad)
    reason(inv / "single_alternative.reason.txt", "Pareto output requires at least two alternatives")

    bad = deepcopy(gary["optimization"])
    del bad["objectives"]["coverage"]
    write(inv / "missing_coverage.json", bad)
    reason(inv / "missing_coverage.reason.txt", "coverage is a required objective")

    bad = deepcopy(gary["optimization"])
    bad["input_design_hash"] = "nope"
    write(inv / "bad_design_hash.json", bad)
    reason(inv / "bad_design_hash.reason.txt", "input_design_hash must be 64 hex chars")

    bad = deepcopy(gary["optimization"])
    bad["schema_version"] = "2.0.0"
    write(inv / "unsupported_major.json", bad)
    reason(inv / "unsupported_major.reason.txt", "major version 2 is unsupported")

    bad = deepcopy(gary["optimization"])
    del bad["selected_alternative_id"]
    write(inv / "missing_selected.json", bad)
    reason(inv / "missing_selected.reason.txt", "selected_alternative_id is required")

    # Invalid calibration
    inv = ROOT / "fixtures" / "invalid" / "calibration"
    bad = deepcopy(gary["calibration"])
    del bad["holdout_validation"]
    write(inv / "missing_holdout.json", bad)
    reason(inv / "missing_holdout.reason.txt", "holdout_validation is required")

    bad = deepcopy(gary["calibration"])
    bad["source_manifest_sha256"] = "abc"
    write(inv / "bad_source_hash.json", bad)
    reason(inv / "bad_source_hash.reason.txt", "source_manifest_sha256 must be 64 hex chars")

    bad = deepcopy(gary["calibration"])
    bad["schema_version"] = "2.1.0"
    write(inv / "unsupported_major.json", bad)
    reason(inv / "unsupported_major.reason.txt", "major version 2 is unsupported")

    bad = deepcopy(gary["calibration"])
    del bad["new_model_version"]
    write(inv / "missing_new_version.json", bad)
    reason(inv / "missing_new_version.reason.txt", "new_model_version is required")

    bad = deepcopy(gary["calibration"])
    bad["email"] = "student@example.com"
    write(inv / "direct_identifier.json", bad)
    reason(inv / "direct_identifier.reason.txt", "direct identifiers are forbidden")

    # Invalid actuation
    inv = ROOT / "fixtures" / "invalid" / "actuation"
    bad = deepcopy(gary["actuation_request"])
    bad["source_path"] = "browser_direct"
    write(inv / "browser_direct.json", bad)
    reason(inv / "browser_direct.reason.txt", "browser-direct path is not an allowed source_path")

    bad = deepcopy(gary["actuation_request"])
    del bad["identity"]
    write(inv / "missing_identity.json", bad)
    reason(inv / "missing_identity.reason.txt", "authenticated identity is required")

    bad = deepcopy(gary["actuation_request"])
    bad["schema_version"] = "2.0.0"
    write(inv / "unsupported_major.json", bad)
    reason(inv / "unsupported_major.reason.txt", "major version 2 is unsupported")

    bad = deepcopy(gary["actuation_receipt"])
    bad["real_actuation_enabled"] = False
    bad["applied"] = True
    write(inv / "applied_while_disabled.json", bad)
    reason(inv / "applied_while_disabled.reason.txt", "applied cannot be true when real actuation is disabled")

    bad = deepcopy(gary["actuation_receipt"])
    bad["e2_claimed"] = True
    write(inv / "e2_claimed.json", bad)
    reason(inv / "e2_claimed.reason.txt", "e2_claimed must remain false")

    hashes = {r["site_id"]: r["hashes"] for r in bundle["results"]}
    write(
        ROOT / "artifacts" / "closed_loop_v2" / "FIXTURE_HASHES.json",
        {
            "source_manifest_sha256": bundle["source_manifest_sha256"],
            "campuses": hashes,
            "loop_gates": {
                k: bundle[k]
                for k in bundle
                if k not in {"results"}
            },
        },
    )
    print(json.dumps({"ok": True, "sha_gary_design": sha256_obj(gary["design"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
