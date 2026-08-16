"""Researcher CLI — runs real adapter probes + OULU/NVIDIA reproduction targets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.external_reproduction.adapters.probe import probe_all, write_probe
from research.external_reproduction.claim_firewall import enforce_firewall
from research.external_reproduction.oulu001_fr3_mmwave import write_artifact_pack as write_oulu001
from research.external_reproduction.oulu002_cfmimo_isac import write_artifact_pack as write_oulu002


TARGETS_DIR = ROOT / "research" / "external_reproduction" / "targets"
ART_DIR = ROOT / "artifacts" / "external_reproduction" / "C_PKT_002"


def cmd_probe(_: argparse.Namespace) -> int:
    out = ART_DIR / "ADAPTER_PROBE.json"
    payload = write_probe(out)
    # also mirror under research
    write_probe(ROOT / "research/external_reproduction/ADAPTER_PROBE.json")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_env(_: argparse.Namespace) -> int:
    path = ROOT / "research/external_reproduction/NVIDIA_6G_ENVIRONMENT.json"
    print(path.read_text(encoding="utf-8"))
    return 0 if path.is_file() else 1


def cmd_run(args: argparse.Namespace) -> int:
    target = args.target.upper()
    ART_DIR.mkdir(parents=True, exist_ok=True)
    probe = probe_all()
    (ART_DIR / "ADAPTER_PROBE.json").write_text(json.dumps(probe, indent=2) + "\n")

    if target == "OULU-001":
        suite = write_oulu001(TARGETS_DIR / "OULU-001")
        write_oulu001(ART_DIR / "OULU-001", suite)
    elif target == "OULU-002":
        suite = write_oulu002(TARGETS_DIR / "OULU-002")
        write_oulu002(ART_DIR / "OULU-002", suite)
    elif target == "ALL":
        s1 = write_oulu001(TARGETS_DIR / "OULU-001")
        write_oulu001(ART_DIR / "OULU-001", s1)
        s2 = write_oulu002(TARGETS_DIR / "OULU-002")
        write_oulu002(ART_DIR / "OULU-002", s2)
        suite = {
            "OULU-001": s1["classification"],
            "OULU-002": s2["classification"],
            "IMPROVED_STATE_OF_ART": False,
        }
    else:
        prep = TARGETS_DIR / target / "PREPARATION_SPEC.json"
        if not prep.is_file():
            print(json.dumps({"ok": False, "error": f"unknown or unprepared target {target}"}))
            return 1
        suite = enforce_firewall(
            {
                "target_id": target,
                "classification": "PREPARATION_ONLY",
                "note": "C5 preparation only — full execute deferred",
                "IMPROVED_STATE_OF_ART": False,
            }
        )
        print(json.dumps(suite, indent=2))
        return 0

    # WAIKE handoff only if DIGITAL_REPRODUCTION_PASS
    if target == "ALL":
        classifications = [
            suite["OULU-001"]["classification"],
            suite["OULU-002"]["classification"],
        ]
        classification_payload = {
            "OULU-001": suite["OULU-001"]["classification"],
            "OULU-002": suite["OULU-002"]["classification"],
        }
    elif isinstance(suite.get("classification"), dict):
        classifications = [suite["classification"]["classification"]]
        classification_payload = suite["classification"]["classification"]
    else:
        classifications = [suite.get("classification")]
        classification_payload = suite.get("classification")

    summary = enforce_firewall(
        {
            "ok": True,
            "target": target,
            "classification": classification_payload,
            "adapter_any_available": probe["any_nvidia_or_sionna_backend_available"],
            "IMPROVED_STATE_OF_ART": False,
            "PHYSICAL": False,
            "OTA": False,
            "6G_CERTIFIED": False,
            "CARRIER_ACCEPTED": False,
            "waike_handoff": False,
        }
    )

    if any(c == "DIGITAL_REPRODUCTION_PASS" for c in classifications):
        handoff = ART_DIR / "WAIKE_HANDOFF_PACKET.json"
        # Still: only emit if PASS; do not edit WAIKE repo
        handoff.write_text(
            json.dumps(
                {
                    "emit": True,
                    "reason": "at least one target earned DIGITAL_REPRODUCTION_PASS",
                    "classifications": classifications,
                    "waike_repo_edited": False,
                    "IMPROVED_STATE_OF_ART": False,
                },
                indent=2,
            )
            + "\n"
        )
        summary["waike_handoff"] = True
    else:
        (ART_DIR / "WAIKE_HANDOFF_SKIPPED.json").write_text(
            json.dumps(
                {
                    "emit": False,
                    "reason": "DIGITAL_REPRODUCTION_PASS not earned; no WAIKE handoff",
                    "classifications": classifications,
                    "waike_repo_edited": False,
                },
                indent=2,
            )
            + "\n"
        )

    (ART_DIR / "LAST_RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe").set_defaults(func=cmd_probe)
    sub.add_parser("env").set_defaults(func=cmd_env)
    run_p = sub.add_parser("run")
    run_p.add_argument("--target", required=True, help="OULU-001|OULU-002|ALL|NVIDIA-001|...")
    run_p.set_defaults(func=cmd_run)
    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
