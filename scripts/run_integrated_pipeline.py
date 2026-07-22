#!/usr/bin/env python3
"""One-command Gate 2 integrated pipeline orchestrator."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from validate_contract import ContractError, validate_document  # noqa: E402


COMPONENT_REPOS = [
    "edge-io-measurement-node",
    "7gc-digital-twin",
    "spectrumx-ai-ran-gary",
    "ntn-resilience-sim",
    "readygary-6g-beam-selection",
]

AIRAN_POLICIES = [
    "static_uniform",
    "network_only",
    "service_priority",
    "optimization_based",
    "twin_informed",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def run_cmd(
    cmd: list[str],
    *,
    cwd: Path,
    log: list[dict[str, Any]],
    env: dict[str, str] | None = None,
    timeout: int = 600,
) -> subprocess.CompletedProcess[str]:
    started = time.perf_counter()
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=merged,
        timeout=timeout,
    )
    entry = {
        "command": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "duration_s": time.perf_counter() - started,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }
    log.append(entry)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def load_repo_lock(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_repo_lock(
    repos_root: Path,
    lock: dict[str, Any],
    *,
    strict: bool,
) -> tuple[dict[str, str], list[str]]:
    shas: dict[str, str] = {}
    warnings: list[str] = []
    for name, meta in lock.get("components", {}).items():
        repo = repos_root / name
        if not repo.is_dir():
            msg = f"Missing repository path: {repo}"
            if meta.get("required", True) or strict:
                raise RuntimeError(msg)
            warnings.append(msg)
            continue
        actual = git_sha(repo)
        shas[name] = actual
        expected = meta.get("commit")
        if expected and actual != expected:
            msg = (
                f"NON-REPRODUCIBLE: {name} commit mismatch "
                f"lock={expected} actual={actual}"
            )
            if strict:
                raise RuntimeError(msg)
            warnings.append(msg)
            print(f"WARNING: {msg}", file=sys.stderr)
    return shas, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Gate 2 integrated pipeline")
    parser.add_argument("--edge-input", required=True)
    parser.add_argument("--repos-root", default=str(ROOT.parent))
    parser.add_argument("--output-root", default=str(ROOT / "results" / "integrated"))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--deploy-policy", default="twin_informed")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    repos_root = Path(args.repos_root).resolve()
    schema_dir = ROOT / "contracts"
    edge_input = Path(args.edge_input).resolve()
    lock = load_repo_lock(ROOT / "integration" / "repo-lock.json")

    command_log: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []
    started_at = utc_now()

    try:
        component_shas, lock_warnings = verify_repo_lock(
            repos_root, lock, strict=args.strict
        )
        warnings.extend(lock_warnings)

        # Validate edge input
        edge_doc = json.loads(edge_input.read_text(encoding="utf-8"))
        validate_document(
            edge_doc,
            schema_dir,
            expected_schema_name="gunnchos.edge_measurement_batch",
            enforce_privacy=True,
        )
        run_id = edge_doc["run_id"]
        site_id = edge_doc["site_id"]
        out_dir = Path(args.output_root).resolve() / run_id
        out_dir.mkdir(parents=True, exist_ok=True)

        env_txt = out_dir / "environment.txt"
        env_txt.write_text(
            "\n".join(
                [
                    f"os={platform.platform()}",
                    f"arch={platform.machine()}",
                    f"python={platform.python_version()}",
                    f"strict={args.strict}",
                    f"repos_root={repos_root}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        edge_out = out_dir / "01_edge_measurements.json"
        edge_repo = repos_root / "edge-io-measurement-node"
        run_cmd(
            [
                sys.executable,
                "-m",
                "edge_io_node",
                "export-to-7gc",
                str(edge_input),
                "--output",
                str(edge_out),
                "--schema-dir",
                str(schema_dir),
            ],
            cwd=edge_repo,
            log=command_log,
            env={"PYTHONPATH": str(edge_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )

        twin_repo = repos_root / "7gc-digital-twin"
        run_cmd(
            [
                sys.executable,
                "-m",
                "seven_gc_twin",
                "ingest-edge",
                "--input",
                str(edge_out),
                "--site",
                site_id,
                "--run-id",
                run_id,
                "--schema-dir",
                str(schema_dir),
            ],
            cwd=twin_repo,
            log=command_log,
            env={"PYTHONPATH": str(twin_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )

        twin_out = out_dir / "02_twin_state.json"
        run_cmd(
            [
                sys.executable,
                "-m",
                "seven_gc_twin",
                "build-twin-state",
                "--input",
                str(edge_out),
                "--run-id",
                run_id,
                "--site",
                site_id,
                "--output",
                str(twin_out),
                "--schema-dir",
                str(schema_dir),
            ],
            cwd=twin_repo,
            log=command_log,
            env={"PYTHONPATH": str(twin_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )
        run_cmd(
            [
                sys.executable,
                "-m",
                "seven_gc_twin",
                "validate-twin-state",
                str(twin_out),
                "--schema-dir",
                str(schema_dir),
            ],
            cwd=twin_repo,
            log=command_log,
            env={"PYTHONPATH": str(twin_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )

        airan_repo = repos_root / "spectrumx-ai-ran-gary"
        airan_paths: dict[str, Path] = {}
        for policy in AIRAN_POLICIES:
            out = out_dir / f"03_airan_{policy.replace('_based','')}_decision.json"
            # Keep required filenames
            name_map = {
                "static_uniform": "03_airan_static_decision.json",
                "network_only": "03_airan_network_only_decision.json",
                "service_priority": "03_airan_service_priority_decision.json",
                "optimization_based": "03_airan_optimization_decision.json",
                "twin_informed": "03_airan_twin_informed_decision.json",
            }
            out = out_dir / name_map[policy]
            run_cmd(
                [
                    sys.executable,
                    "-m",
                    "airan_research",
                    "evaluate-policy",
                    "--twin-state",
                    str(twin_out),
                    "--policy",
                    policy,
                    "--output",
                    str(out),
                    "--schema-dir",
                    str(schema_dir),
                    "--seed",
                    str(args.seed),
                ],
                cwd=airan_repo,
                log=command_log,
                env={
                    "PYTHONPATH": str(airan_repo / "src"),
                    "GATE2_CONTRACTS_DIR": str(schema_dir),
                },
            )
            run_cmd(
                [
                    sys.executable,
                    "-m",
                    "airan_research",
                    "validate-decision",
                    str(out),
                    "--schema-dir",
                    str(schema_dir),
                ],
                cwd=airan_repo,
                log=command_log,
                env={
                    "PYTHONPATH": str(airan_repo / "src"),
                    "GATE2_CONTRACTS_DIR": str(schema_dir),
                },
            )
            airan_paths[policy] = out

        deploy = airan_paths[args.deploy_policy]
        ntn_repo = repos_root / "ntn-resilience-sim"
        resilience_out = out_dir / "04_resilience_decision.json"
        run_cmd(
            [
                sys.executable,
                "-m",
                "ntn_resilience",
                "decide",
                "--twin-state",
                str(twin_out),
                "--airan-decision",
                str(deploy),
                "--output",
                str(resilience_out),
                "--schema-dir",
                str(schema_dir),
                "--policy",
                "service_aware_multi_access",
            ],
            cwd=ntn_repo,
            log=command_log,
            env={"PYTHONPATH": str(ntn_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )
        run_cmd(
            [
                sys.executable,
                "-m",
                "ntn_resilience",
                "validate-decision",
                str(resilience_out),
                "--schema-dir",
                str(schema_dir),
            ],
            cwd=ntn_repo,
            log=command_log,
            env={"PYTHONPATH": str(ntn_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )

        bench_out = out_dir / "benchmark_results.csv"
        run_cmd(
            [
                sys.executable,
                "-m",
                "airan_research",
                "benchmark",
                "--twin-state",
                str(twin_out),
                "--output",
                str(bench_out),
                "--schema-dir",
                str(schema_dir),
                "--repetitions",
                "3",
                "--warmup",
                "1",
                "--seed",
                str(args.seed),
            ],
            cwd=airan_repo,
            log=command_log,
            env={
                "PYTHONPATH": str(airan_repo / "src"),
                "GATE2_CONTRACTS_DIR": str(schema_dir),
            },
        )

        abl_out = out_dir / "ablation_results.csv"
        run_cmd(
            [
                sys.executable,
                "-m",
                "airan_research",
                "ablation",
                "--twin-state",
                str(twin_out),
                "--output",
                str(abl_out),
                "--schema-dir",
                str(schema_dir),
                "--seed",
                str(args.seed),
            ],
            cwd=airan_repo,
            log=command_log,
            env={
                "PYTHONPATH": str(airan_repo / "src"),
                "GATE2_CONTRACTS_DIR": str(schema_dir),
            },
        )

        sens_out = out_dir / "sensitivity_results.csv"
        run_cmd(
            [
                sys.executable,
                "-m",
                "ntn_resilience",
                "sensitivity",
                "--twin-state",
                str(twin_out),
                "--airan-decision",
                str(deploy),
                "--output",
                str(sens_out),
                "--schema-dir",
                str(schema_dir),
            ],
            cwd=ntn_repo,
            log=command_log,
            env={"PYTHONPATH": str(ntn_repo / "src"), "GATE2_CONTRACTS_DIR": str(schema_dir)},
        )

        # ReadyGary optional
        readygary_used = False
        rg = repos_root / "readygary-6g-beam-selection"
        if rg.is_dir():
            warnings.append(
                "ReadyGary present but optional provider not required for Gate 2 path; continuing without beam actions."
            )

        resilience_doc = json.loads(resilience_out.read_text(encoding="utf-8"))
        deploy_doc = json.loads(deploy.read_text(encoding="utf-8"))

        # Checksums for artifacts
        artifact_names = [
            "01_edge_measurements.json",
            "02_twin_state.json",
            "03_airan_static_decision.json",
            "03_airan_network_only_decision.json",
            "03_airan_service_priority_decision.json",
            "03_airan_optimization_decision.json",
            "03_airan_twin_informed_decision.json",
            "04_resilience_decision.json",
            "benchmark_results.csv",
            "ablation_results.csv",
            "sensitivity_results.csv",
            "environment.txt",
        ]
        checksum_lines = []
        output_hashes = {}
        for name in artifact_names:
            path = out_dir / name
            digest = sha256_file(path)
            output_hashes[name] = digest
            checksum_lines.append(f"{digest}  {name}")
        checksum_path = out_dir / "checksums.sha256"
        checksum_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

        # Verify checksums
        run_cmd(
            [sys.executable, str(ROOT / "scripts" / "verify_checksums.py"), str(checksum_path)],
            cwd=out_dir,
            log=command_log,
        )

        field_kit_sha = git_sha(ROOT)
        component_shas["gunnchos-7gc-ai-ran-field-kit"] = field_kit_sha

        validation_report = {
            "edge": True,
            "twin": True,
            "airan_policies": list(AIRAN_POLICIES),
            "resilience": True,
            "checksums": True,
        }
        (out_dir / "validation_report.json").write_text(
            json.dumps(validation_report, indent=2) + "\n", encoding="utf-8"
        )

        # Gate status evaluation
        run_cmd(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_gate2_status.py"),
                "--run-dir",
                str(out_dir),
                "--output",
                str(out_dir / "gate2_status.json"),
            ],
            cwd=ROOT,
            log=command_log,
        )
        gate_status = json.loads((out_dir / "gate2_status.json").read_text(encoding="utf-8"))

        manifest = {
            "schema_name": "gunnchos.integrated_run_manifest",
            "schema_version": "1.0.0",
            "run_id": run_id,
            "site_id": site_id,
            "component_commits": {
                k: v for k, v in component_shas.items() if k != "gunnchos-7gc-ai-ran-field-kit"
            },
            "schema_versions": {
                "edge_measurement_batch": "1.0.0",
                "twin_state_bundle": "1.0.0",
                "airan_decision_bundle": "1.0.0",
                "resilience_decision_bundle": "1.0.0",
                "integrated_run_manifest": "1.0.0",
            },
            "configuration_hashes": {
                "repo_lock": sha256_file(ROOT / "integration" / "repo-lock.json"),
            },
            "input_hashes": {"edge_input": sha256_file(edge_input)},
            "output_hashes": output_hashes,
            "random_seeds": {"airan": args.seed},
            "environment": {
                "os": platform.platform(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "dependency_lock_hashes": {
                    "field_kit_requirements": sha256_file(ROOT / "requirements.txt")
                    if (ROOT / "requirements.txt").exists()
                    else "0" * 64,
                },
            },
            "commands_executed": [
                {
                    "command": e["command"],
                    "returncode": e["returncode"],
                    "duration_s": e["duration_s"],
                    "cwd": e["cwd"],
                }
                for e in command_log
            ],
            "started_at": started_at,
            "completed_at": utc_now(),
            "validation_results": validation_report,
            "test_results": {"orchestrator": "commands_executed"},
            "evidence_levels": {
                "edge_input": edge_doc.get("evidence_level"),
                "twin": json.loads(twin_out.read_text())["evidence_level"],
            },
            "readygary_used": readygary_used,
            "failures": failures,
            "warnings": warnings,
            "field_kit_runtime_sha": field_kit_sha,
            "gate2_status": gate_status["status"],
            "selected_airan_policy": args.deploy_policy,
            "selected_resilience_mode": resilience_doc["selected_mode"],
        }
        manifest_path = out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        validate_document(
            manifest,
            schema_dir,
            expected_schema_name="gunnchos.integrated_run_manifest",
            enforce_privacy=False,
        )

        (out_dir / "command_log.txt").write_text(
            "\n\n".join(
                f"$ {e['command']}\nrc={e['returncode']} dur={e['duration_s']:.4f}s\n"
                f"stdout:\n{e['stdout_tail']}\nstderr:\n{e['stderr_tail']}"
                for e in command_log
            )
            + "\n",
            encoding="utf-8",
        )

        run_cmd(
            [
                sys.executable,
                str(ROOT / "scripts" / "generate_integrated_report.py"),
                "--run-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            log=command_log,
        )

        # refresh checksums to include manifest/report
        extra = [
            "manifest.json",
            "validation_report.json",
            "gate2_status.json",
            "command_log.txt",
            "integrated_report.md",
            "reproduction_log.md",
        ]
        lines = checksum_path.read_text(encoding="utf-8").splitlines()
        for name in extra:
            path = out_dir / name
            if path.exists():
                lines.append(f"{sha256_file(path)}  {name}")
        checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(
            json.dumps(
                {
                    "ok": True,
                    "run_id": run_id,
                    "output_dir": str(out_dir),
                    "gate2_status": gate_status["status"],
                    "selected_airan_policy": args.deploy_policy,
                    "selected_resilience_mode": resilience_doc["selected_mode"],
                    "evidence_level": edge_doc.get("evidence_level"),
                },
                indent=2,
            )
        )
        return 0 if gate_status["status"] != "FAIL" else 2

    except (ContractError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"PIPELINE FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
