#!/usr/bin/env python3
"""Generate Gate 4 figures from raw CSV/JSON artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import read_csv, sha256_file, utc_now, write_json


def generate(raw_results_dir: Path, output_dir: Path) -> dict:
    rows = read_csv(raw_results_dir / "sensitivity_results.csv")
    values = []
    for row in rows:
        try:
            values.append((row.get("condition") or "unknown", float(row.get("value") or 0.0)))
        except ValueError:
            values.append((row.get("condition") or "unknown", 0.0))
    width = 900
    height = 360
    bar_w = max(8, int((width - 120) / max(1, len(values))))
    max_val = max([v for _, v in values] or [1.0]) or 1.0
    bars = []
    for i, (label, value) in enumerate(values):
        bar_h = int((value / max_val) * 240)
        x = 80 + i * bar_w
        y = 300 - bar_h
        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_w - 2}" height="{bar_h}" fill="#3366cc">'
            f"<title>{label}: {value}</title></rect>"
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="360" role="img">'
        "<title>Gate 4 sensitivity dry-run figure</title>"
        '<rect width="100%" height="100%" fill="white"/>'
        '<text x="20" y="30" font-family="sans-serif" font-size="18">Gate 4 sensitivity results</text>'
        '<line x1="70" y1="300" x2="870" y2="300" stroke="black"/>'
        '<line x1="70" y1="60" x2="70" y2="300" stroke="black"/>'
        + "".join(bars)
        + '<text x="20" y="340" font-family="sans-serif" font-size="12">Generated from raw CSV only; dry-run values are not physical measurements.</text>'
        + "</svg>\n"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_path = output_dir / "gate4_sensitivity.svg"
    svg_path.write_text(svg, encoding="utf-8")
    provenance = {
        "schema_name": "gunnchos.gate4_figure_provenance",
        "schema_version": "1.0.0",
        "figure": str(svg_path),
        "source_files": [str(raw_results_dir / "sensitivity_results.csv")],
        "source_checksums": {
            "sensitivity_results.csv": sha256_file(raw_results_dir / "sensitivity_results.csv")
            if (raw_results_dir / "sensitivity_results.csv").is_file()
            else None
        },
        "generated_at": utc_now(),
        "renderer": "stdlib_svg_writer",
    }
    write_json(output_dir / "gate4_figure_provenance.json", provenance)
    return provenance


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-results-dir", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args(argv)
    result = generate(Path(args.raw_results_dir), Path(args.output_dir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
