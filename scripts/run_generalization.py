#!/usr/bin/env python3
"""Download, verify, preprocess, and evaluate public generalization datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generalization.adapters.nordicdat.adapter import (  # noqa: E402
    create_nordicdat_adapter,
    load_config,
    summarize_domain_shift,
    write_normalized_output,
)
from scripts.gate3_common import sha256_file, write_json  # noqa: E402

SUPPORTED = {"nordicdat"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def config_path(dataset: str) -> Path:
    if dataset not in SUPPORTED:
        raise SystemExit(f"Unsupported DATASET={dataset!r}; supported: {sorted(SUPPORTED)}")
    return ROOT / "generalization/configs" / f"{dataset}.yaml"


def load_dataset_config(dataset: str) -> dict[str, Any]:
    with config_path(dataset).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def manifest_path(dataset: str) -> Path:
    return ROOT / "generalization/manifests" / f"{dataset}.json"


def _fetch_url(url: str, dest: Path) -> None:
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, timeout=120, context=ctx) as resp:
            dest.write_bytes(resp.read())
            return
    except Exception as exc:
        print(f"urllib download failed ({exc}); retrying with curl")
    result = subprocess.run(
        ["curl", "-fsSL", "-o", str(dest), url],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "curl download failed")


def download(dataset: str) -> dict[str, Any]:
    cfg = load_dataset_config(dataset)
    source_path = ROOT / cfg["paths"]["source_file"]
    source_path.parent.mkdir(parents=True, exist_ok=True)
    url = cfg["source"]["download_url"]
    print(f"Downloading {dataset} from {url}")
    _fetch_url(url, source_path)
    data = source_path.read_bytes()
    checksum = sha256_file(source_path)
    md5 = hashlib.md5(data).hexdigest()  # noqa: S324 — upstream publishes MD5
    manifest = {
        "dataset_name": dataset,
        "downloaded_at": _utc_now(),
        "source_url": url,
        "local_path": str(source_path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": checksum,
        "md5": md5,
        "upstream_md5": cfg["checksums"].get("upstream_md5"),
        "license": cfg["license"]["name"],
        "evidence_class": cfg["evidence_class"],
        "physical_pilot_data": False,
        "generalization_evidence_pass": False,
    }
    write_json(manifest_path(dataset), manifest)
    return manifest


def verify(dataset: str) -> dict[str, Any]:
    cfg = load_dataset_config(dataset)
    source_path = ROOT / cfg["paths"]["source_file"]
    if not source_path.is_file():
        return {"ok": False, "errors": [f"missing source file: {source_path}"]}
    errors: list[str] = []
    checksum = sha256_file(source_path)
    md5 = hashlib.md5(source_path.read_bytes()).hexdigest()  # noqa: S324
    expected_md5 = cfg["checksums"].get("upstream_md5")
    if expected_md5 and md5 != expected_md5:
        errors.append(f"md5 mismatch: expected {expected_md5}, got {md5}")
    if cfg["license"]["verification_status"] != "VERIFIED_LICENSE":
        errors.append("license not VERIFIED_LICENSE in config")
    result = {
        "ok": not errors,
        "dataset": dataset,
        "path": str(source_path.relative_to(ROOT)),
        "sha256": checksum,
        "md5": md5,
        "bytes": source_path.stat().st_size,
        "errors": errors,
        "evidence_class": cfg["evidence_class"],
        "physical_pilot_data": False,
    }
    manifest = manifest_path(dataset)
    if manifest.is_file():
        existing = json.loads(manifest.read_text(encoding="utf-8"))
        existing["verified_at"] = _utc_now()
        existing["sha256"] = checksum
        existing["md5"] = md5
        existing["verify_ok"] = result["ok"]
        write_json(manifest, existing)
    return result


def preprocess(dataset: str) -> dict[str, Any]:
    if dataset != "nordicdat":
        raise SystemExit(f"preprocess not implemented for {dataset}")
    verify_result = verify(dataset)
    if not verify_result["ok"]:
        raise SystemExit(f"verify failed before preprocess: {verify_result['errors']}")
    adapter = create_nordicdat_adapter()
    normalized = adapter.load()
    cfg = load_config()
    out_path = ROOT / cfg["paths"]["normalized_output"]
    write_normalized_output(out_path, normalized)
    report = {
        "dataset": dataset,
        "preprocessed_at": _utc_now(),
        "output_path": str(out_path.relative_to(ROOT)),
        "output_sha256": sha256_file(out_path),
        "row_count_raw": normalized.metadata["row_count_raw"],
        "row_count_normalized": normalized.metadata["row_count_normalized"],
        "dropped_records": normalized.metadata["row_count_raw"] - normalized.metadata["row_count_normalized"],
        "evidence_class": cfg["evidence_class"],
        "physical_pilot_data": False,
        "generalization_evidence_pass": False,
    }
    write_json(out_path.with_name("preprocess_report.json"), report)
    return report


def evaluate(dataset: str) -> dict[str, Any]:
    if dataset != "nordicdat":
        raise SystemExit(f"evaluate not implemented for {dataset}")
    cfg = load_config()
    normalized_path = ROOT / cfg["paths"]["normalized_output"]
    if not normalized_path.is_file():
        raise SystemExit(f"run preprocess first; missing {normalized_path}")
    payload = json.loads(normalized_path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    report = summarize_domain_shift(records)
    report.update(
        {
            "dataset": dataset,
            "evaluated_at": _utc_now(),
            "record_count": len(records),
            "citation": cfg["citation"].strip(),
            "license": cfg["license"]["name"],
            "source_url": cfg["source"]["url"],
            "limitations": cfg["limitations"],
            "label": "public_dataset_evidence_separate_from_physical_pilot",
        }
    )
    out_path = ROOT / cfg["paths"]["evaluation_output"]
    write_json(out_path, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("download", "verify", "preprocess", "evaluate"):
        p = sub.add_parser(name)
        p.add_argument("--dataset", required=True)
    args = parser.parse_args(argv)
    dataset = args.dataset
    if args.cmd == "download":
        result = download(dataset)
    elif args.cmd == "verify":
        result = verify(dataset)
    elif args.cmd == "preprocess":
        result = preprocess(dataset)
    else:
        result = evaluate(dataset)
    print(json.dumps(result, indent=2))
    if isinstance(result, dict) and result.get("ok") is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
