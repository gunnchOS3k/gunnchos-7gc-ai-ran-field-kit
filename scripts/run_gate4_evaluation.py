#!/usr/bin/env python3
"""One-command Gate 4 evaluation/readiness orchestrator."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import build_splits, synthetic_manifest  # noqa: E402
from evaluate_gate4_status import evaluate as evaluate_status  # noqa: E402
from gate4_common import (  # noqa: E402
    evaluation_label,
    evidence_level,
    load_dataset_manifest,
    load_dataset_rows,
    utc_now,
    write_json,
)
from run_ablations import run as run_ablations  # noqa: E402
from run_baselines import run as run_baselines  # noqa: E402
from run_sensitivity import run as run_sensitivity  # noqa: E402
from calculate_uncertainty import calculate as calculate_uncertainty  # noqa: E402
from analyze_failure_boundaries import analyze as analyze_failure_boundaries  # noqa: E402
from generate_negative_results import generate as generate_negative_results  # noqa: E402
from generate_tables import generate as generate_tables  # noqa: E402
from generate_figures import generate as generate_figures  # noqa: E402
from generate_gate4_report import generate as generate_report  # noqa: E402


def git_sha(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    except Exception:
        return "0" * 40


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=None, help="Path to a dataset manifest")
    p.add_argument("--repos-root", default=str(ROOT.parent))
    p.add_argument("--output-root", default=str(ROOT / "results" / "gate4"))
    p.add_argument("--strict", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Create a synthetic infrastructure-validation manifest")
    args = p.parse_args(argv)

    out_root = Path(args.output_root)
    out_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_root / f"gate4-run-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    experiment_id = f"gate4-{stamp}"

    if args.dataset:
        dataset_path = Path(args.dataset).resolve()
    else:
        dataset_path = run_dir / "synthetic_infrastructure_dataset_manifest.json"
        args.dry_run = True
    if args.dry_run and not dataset_path.exists():
        write_json(dataset_path, synthetic_manifest(dataset_path))

    manifest = load_dataset_manifest(dataset_path)
    rows = load_dataset_rows(manifest)
    sample_count = len(rows) or int(manifest.get("n_sessions") or 0)
    experiment_manifest = {
        "schema_name": "gunnchos.gate4_experiment_manifest",
        "schema_version": "1.0.0",
        "experiment_id": experiment_id,
        "dataset_manifest": str(dataset_path),
        "evidence_level": evidence_level(manifest),
        "evaluation_label": evaluation_label(manifest),
        "sample_count": sample_count,
        "created_at": utc_now(),
        "strict": bool(args.strict),
        "repository_commits": {
            "gunnchos-7gc-ai-ran-field-kit": git_sha(ROOT),
            "edge-io-measurement-node": git_sha(Path(args.repos_root) / "edge-io-measurement-node"),
            "7gc-digital-twin": git_sha(Path(args.repos_root) / "7gc-digital-twin"),
            "spectrumx-ai-ran-gary": git_sha(Path(args.repos_root) / "spectrumx-ai-ran-gary"),
            "ntn-resilience-sim": git_sha(Path(args.repos_root) / "ntn-resilience-sim"),
            "readygary-6g-beam-selection": git_sha(Path(args.repos_root) / "readygary-6g-beam-selection"),
        },
        "configs": {
            "baselines": str(ROOT / "evaluation" / "configs" / "baselines.yaml"),
            "held_out_scenarios": str(ROOT / "evaluation" / "configs" / "held_out_scenarios.yaml"),
            "ablations": str(ROOT / "evaluation" / "configs" / "ablations.yaml"),
            "sensitivity": str(ROOT / "evaluation" / "configs" / "sensitivity.yaml"),
            "metrics": str(ROOT / "evaluation" / "configs" / "metrics.yaml"),
        },
        "limitations": [
            "Dry-run datasets are infrastructure_validation_only.",
            "Synthetic/calibration-only data are insufficient_sample_size_for_inference.",
        ],
    }
    write_json(run_dir / "experiment_manifest.json", experiment_manifest)

    allow_small = bool(args.dry_run or evaluation_label(manifest) == "infrastructure_validation_only")
    split_summary = build_splits(manifest, run_dir / "splits", allow_small=allow_small)
    if not split_summary["ok"] and args.strict and not allow_small:
        write_json(run_dir / "gate4_status.json", {"gate4_status": "FAIL", "split_summary": split_summary})
        print(json.dumps({"ok": False, "run_dir": str(run_dir), "gate4_status": "FAIL"}, indent=2))
        return 2

    raw_dir = run_dir / "raw_results"
    reports_dir = run_dir / "reports"
    run_baselines(manifest, raw_dir / "baseline_results.csv", experiment_id=experiment_id)
    run_ablations(manifest, raw_dir / "ablation_results.csv", experiment_id=experiment_id)
    run_sensitivity(manifest, raw_dir / "sensitivity_results.csv", experiment_id=experiment_id)
    calculate_uncertainty(
        manifest,
        raw_dir / "baseline_results.csv",
        raw_dir / "uncertainty_report.json",
        seed=0,
    )
    analyze_failure_boundaries(
        manifest,
        raw_dir / "failure_boundaries.csv",
        reports_dir / "FAILURE_BOUNDARY_REPORT.md",
        experiment_id=experiment_id,
    )
    generate_negative_results(manifest, reports_dir / "NEGATIVE_RESULTS_REGISTER.md", experiment_id=experiment_id)
    generate_tables(raw_dir, run_dir / "tables")
    generate_figures(raw_dir, run_dir / "figures")

    # Seed the report path so artifact completeness can be evaluated, then overwrite
    # with the final status-aware report below.
    (reports_dir / "GATE4_EVALUATION_REPORT.md").write_text(
        "# Gate 4 Evaluation Report\n\nStatus pending during generation.\n",
        encoding="utf-8",
    )
    status = evaluate_status(dataset_path, run_dir, run_dir / "gate4_status.json")
    report = generate_report(run_dir, run_dir / "gate4_status.json", reports_dir)
    status = evaluate_status(dataset_path, run_dir, run_dir / "gate4_status.json")

    summary = {
        "ok": status["gate4_status"] != "FAIL",
        "run_dir": str(run_dir),
        "gate4_status": status["gate4_status"],
        "evaluation_label": status["evaluation_label"],
        "inference_label": status["inference_label"],
        "sample_count": status["sample_count"],
        "report": str(reports_dir / "GATE4_EVALUATION_REPORT.md"),
        "report_schema": report.get("schema_name"),
    }
    print(json.dumps(summary, indent=2))
    if status["gate4_status"] == "FAIL":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
