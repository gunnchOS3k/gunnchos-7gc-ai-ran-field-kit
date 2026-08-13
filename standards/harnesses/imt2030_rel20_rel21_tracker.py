"""Executable IMT-2030 / Rel-20 / Rel-21 tracker using pinned in-repo snapshots.

Never claims STANDARDIZED_6G or CARRIER_ACCEPTED. GATE_8_PASS remains forbidden.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STD = ROOT / "standards"

STANDARDIZED_6G = False
CARRIER_ACCEPTED = False
GATE_8_PASS = False

CLAIM_BOUNDARY = (
    "Pinned-standards tracker only. Rel-20 is 5G-Advanced + early 6G studies. "
    "Rel-21 is TRACKER_ONLY. No standardized 6G, no carrier acceptance, "
    "no IMT-2030 compliance claim. RM520N-GL is not NTN and not 6G."
)

REQUIRED_SNAPSHOTS = (
    "itu-imt-2030-2026-08-07.md",
    "3gpp-rel20-2026-08-07.md",
    "3gpp-rel21-2026-08-13.md",
)

USAGE_SCENARIOS = (
    "immersive_communication",
    "hyper_reliable_low_latency_communication",
    "massive_communication",
    "ubiquitous_connectivity",
    "ai_and_communication",
    "integrated_sensing_and_communication",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def evaluate(out_dir: Path | None = None) -> dict[str, Any]:
    snaps = STD / "source_snapshots"
    missing = [name for name in REQUIRED_SNAPSHOTS if not (snaps / name).is_file()]
    tracker = STD / "requirements" / "imt2030_current_state.yaml"
    mapping = ROOT / "program" / "full_product" / "imt2030_migration_mapping.yaml"
    sources = STD / "sources.yaml"

    rel20 = _read(snaps / "3gpp-rel20-2026-08-07.md") if not missing else ""
    rel21 = _read(snaps / "3gpp-rel21-2026-08-13.md") if (snaps / "3gpp-rel21-2026-08-13.md").is_file() else ""
    itu = _read(snaps / "itu-imt-2030-2026-08-07.md") if (snaps / "itu-imt-2030-2026-08-07.md").is_file() else ""

    checks = {
        "snapshots_present": not missing,
        "tracker_yaml_present": tracker.is_file(),
        "mapping_yaml_present": mapping.is_file(),
        "sources_yaml_present": sources.is_file(),
        "rel20_mentions_5g_advanced": "5G-Advanced" in rel20,
        "rel20_mentions_early_6g_studies": "early 6G studies" in rel20,
        "rel21_tracker_only": "TRACKER_ONLY" in rel21,
        "rel21_forbids_compliance": "No Rel-21 freeze" in rel21 or "no product compliance" in rel21.lower(),
        "itu_m2160_approved": "M.2160" in itu,
        "STANDARDIZED_6G_false": STANDARDIZED_6G is False,
        "CARRIER_ACCEPTED_false": CARRIER_ACCEPTED is False,
        "GATE_8_PASS_false": GATE_8_PASS is False,
    }
    scenarios = {
        name: {
            "mapped": True,
            "os_dependency": "connectivity_orchestrator",
            "future_conformance_method": "pending_normative_specs",
            "STANDARDIZED_6G": False,
            "CARRIER_ACCEPTED": False,
        }
        for name in USAGE_SCENARIOS
    }
    ok = all(checks.values()) and not missing
    report = {
        "schema": "gunnchos.field_kit.imt2030_rel20_rel21_tracker.v1",
        "ok": ok,
        "exit_state": "DIGITALLY_VALIDATED" if ok else "INCOMPLETE_DIGITAL",
        "STANDARDIZED_6G": STANDARDIZED_6G,
        "CARRIER_ACCEPTED": CARRIER_ACCEPTED,
        "GATE_8_PASS": GATE_8_PASS,
        "rel20": {
            "status": "STUDY_OR_NORMATIVE_IN_PROGRESS",
            "role": "5G-Advanced + early 6G studies",
            "snapshot": "3gpp-rel20-2026-08-07.md",
        },
        "rel21": {
            "status": "TRACKER_ONLY",
            "role": "planned normative 6G phase",
            "snapshot": "3gpp-rel21-2026-08-13.md",
            "freeze_claimed": False,
        },
        "usage_scenarios": scenarios,
        "checks": checks,
        "missing_snapshots": missing,
        "rm520n_ntn_claimed": False,
        "rm520n_6g_claimed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "mock": False,
    }
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "IMT2030_REL20_REL21_TRACKER.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    return report


def main() -> int:
    report = evaluate(ROOT / "artifacts" / "standards")
    print("IMT2030_TRACKER_PASS" if report["ok"] else "IMT2030_TRACKER_FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
