"""Regression: Gate 2 must not select stray calibration artifacts via glob/ls."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from select_gate2_run_dir import REQUIRED_MARKERS, main, select_gate2_run_dir  # noqa: E402


def _complete_run(path: Path, run_id: str) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_MARKERS:
        if name == "manifest.json":
            (path / name).write_text(f'{{"run_id": "{run_id}"}}\n', encoding="utf-8")
        elif name == "gate2_status.json":
            (path / name).write_text('{"status": "GATE2_SYSTEM_PASS"}\n', encoding="utf-8")
        else:
            (path / name).write_text("placeholder\n", encoding="utf-8")
    return path


def test_skips_calibration_artifact_without_gate2_status(tmp_path):
    output_root = tmp_path / "integrated"
    calibration = output_root / "calibration-cal-20260722T170604Z"
    calibration.mkdir(parents=True)
    (calibration / "CALIBRATION_INTEGRATED_REPORT.md").write_text("# cal\n", encoding="utf-8")
    intended = _complete_run(
        output_root / "2026-07-22-synthetic-gary-learn-001",
        "2026-07-22-synthetic-gary-learn-001",
    )

    # pathlib.glob / unsorted iteration can surface calibration first.
    glob_first = list(output_root.glob("*"))[0]
    assert glob_first.name in {
        "calibration-cal-20260722T170604Z",
        "2026-07-22-synthetic-gary-learn-001",
    }

    selected = select_gate2_run_dir(output_root)
    assert selected.resolve() == intended.resolve()
    assert selected.name != "calibration-cal-20260722T170604Z"
    assert (selected / "gate2_status.json").is_file()


def test_prefer_run_id_ignores_other_complete_runs(tmp_path):
    output_root = tmp_path / "integrated"
    _complete_run(output_root / "calibration-complete-but-not-this-ci", "other")
    intended = _complete_run(
        output_root / "2026-07-22-synthetic-gary-learn-001",
        "2026-07-22-synthetic-gary-learn-001",
    )
    selected = select_gate2_run_dir(
        output_root, prefer_run_id="2026-07-22-synthetic-gary-learn-001"
    )
    assert selected.resolve() == intended.resolve()


def test_prefer_run_id_fails_when_calibration_is_the_named_dir(tmp_path):
    output_root = tmp_path / "integrated"
    calibration = output_root / "calibration-cal-20260722T170604Z"
    calibration.mkdir(parents=True)
    (calibration / "CALIBRATION_INTEGRATED_REPORT.md").write_text("# cal\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Refusing glob/ls fallback"):
        select_gate2_run_dir(
            output_root, prefer_run_id="calibration-cal-20260722T170604Z"
        )


def test_fails_when_only_calibration_artifact_present(tmp_path):
    output_root = tmp_path / "integrated"
    calibration = output_root / "calibration-cal-20260722T170604Z"
    calibration.mkdir(parents=True)
    (calibration / "CALIBRATION_INTEGRATED_REPORT.md").write_text("# cal\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No complete Gate 2 integrated run"):
        select_gate2_run_dir(output_root)


def test_cli_writes_github_env_and_uses_edge_input(tmp_path):
    output_root = tmp_path / "integrated"
    intended = _complete_run(
        output_root / "2026-07-22-synthetic-gary-learn-001",
        "2026-07-22-synthetic-gary-learn-001",
    )
    (output_root / "calibration-cal-20260722T170604Z").mkdir()
    edge = tmp_path / "edge.json"
    edge.write_text(
        '{"run_id": "2026-07-22-synthetic-gary-learn-001"}\n', encoding="utf-8"
    )
    github_env = tmp_path / "github_env"
    rc = main(
        [
            "--output-root",
            str(output_root),
            "--edge-input",
            str(edge),
            "--github-env",
            str(github_env),
        ]
    )
    assert rc == 0
    env_text = github_env.read_text(encoding="utf-8")
    assert f"RUN_DIR={intended.resolve()}" in env_text


def test_cli_fails_closed_on_stray_calibration_only(tmp_path, capsys):
    output_root = tmp_path / "integrated"
    (output_root / "calibration-cal-20260722T170604Z").mkdir(parents=True)
    rc = main(["--output-root", str(output_root)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "Refusing glob/ls fallback" in err
    assert "calibration-cal-20260722T170604Z" in err
