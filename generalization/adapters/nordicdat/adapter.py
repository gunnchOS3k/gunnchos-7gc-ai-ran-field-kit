"""NordicDat adapter — public wireless QoS generalization evidence.

GENERALIZATION_EVIDENCE_PASS: NOT CLAIMED.
Physical pilot data is never loaded by this adapter.
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from generalization.adapters.base import (
    EvidenceAdapter,
    EvidenceSource,
    LicenseStatus,
    LicenseVerificationError,
    NormalizedRecord,
    load_registry,
    resolve_source,
)

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "generalization/configs/nordicdat.yaml"
REGISTRY_PATH = ROOT / "generalization/EVIDENCE_SOURCE_REGISTRY.yaml"
SOURCE_ID = "nordicdat_qos_public"


def load_config(path: Path | None = None) -> Mapping[str, Any]:
    cfg_path = path or CONFIG_PATH
    with cfg_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_row(row: Mapping[str, str], mapping: Mapping[str, str]) -> dict[str, Any] | None:
    out: dict[str, Any] = {}
    for src, dst in mapping.items():
        raw = row.get(src)
        if dst in {"access_technology", "band_label"}:
            val = (raw or "").strip().upper() or None
            if val and val.startswith("5G"):
                val = "5G"
            out[dst] = val
        elif dst == "service_available":
            out[dst] = str(raw).strip() in {"1", "true", "True"}
        elif dst == "operator_id_anonymized":
            val = _to_float(raw)
            out[dst] = int(val) if val is not None else None
        else:
            out[dst] = _to_float(raw)
    return out


def normalize_csv_rows(
    rows: Sequence[Mapping[str, str]],
    config: Mapping[str, Any],
) -> list[dict[str, Any]]:
    mapping = config["schema_mapping"]
    required = set(config["normalization"]["drop_if_missing"])
    normalized: list[dict[str, Any]] = []
    for row in rows:
        record = _normalize_row(row, mapping)
        if record is None:
            continue
        if any(record.get(field) is None for field in required):
            continue
        normalized.append(record)
    return normalized


class NordicDatAdapter(EvidenceAdapter):
    """Load and normalize NordicDat CSV for public generalization analysis."""

    def __init__(
        self,
        source: EvidenceSource,
        config: Mapping[str, Any] | None = None,
        csv_path: Path | None = None,
    ) -> None:
        super().__init__(source)
        self.config = dict(config or load_config())
        paths = self.config["paths"]
        self.csv_path = csv_path or (ROOT / paths["source_file"])
        if source.license_status != LicenseStatus.VERIFIED_LICENSE:
            raise LicenseVerificationError(
                f"NordicDatAdapter requires VERIFIED_LICENSE; got {source.license_status.value}"
            )

    def load(self) -> NormalizedRecord:
        self.assert_license_verified()
        if not self.csv_path.is_file():
            raise FileNotFoundError(f"NordicDat source file missing: {self.csv_path}")

        with self.csv_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)

        records = normalize_csv_rows(rows, self.config)
        metadata = {
            "dataset_name": self.config["dataset_name"],
            "evidence_class": self.config["evidence_class"],
            "source_id": self.source.id,
            "citation": self.config["citation"].strip(),
            "license": self.config["license"]["name"],
            "row_count_raw": len(rows),
            "row_count_normalized": len(records),
            "physical_pilot_data": False,
            "generalization_evidence_pass": False,
        }
        return NormalizedRecord(
            source_id=self.source.id,
            records=records,
            metadata=metadata,
        )

    def describe(self) -> Mapping[str, Any]:
        return {
            "adapter": "NordicDatAdapter",
            "source_id": self.source.id,
            "license_status": self.source.license_status.value,
            "evidence_class": self.config.get("evidence_class"),
            "csv_path": str(self.csv_path),
            "physical_pilot_data": False,
            "generalization_evidence_pass": False,
        }


def create_nordicdat_adapter(
    registry_path: Path | None = None,
    config: Mapping[str, Any] | None = None,
    csv_path: Path | None = None,
) -> NordicDatAdapter:
    registry = load_registry(registry_path or REGISTRY_PATH)
    source = resolve_source(registry, SOURCE_ID)
    return NordicDatAdapter(source, config=config, csv_path=csv_path)


def summarize_domain_shift(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Compute LTE vs 5G QoS summaries for public domain-shift reporting."""

    def bucket(name: str) -> list[Mapping[str, Any]]:
        return [r for r in records if str(r.get("access_technology", "")).upper() == name]

    def stats(values: Sequence[float]) -> dict[str, float | int | None]:
        if not values:
            return {"count": 0, "mean": None, "median": None, "p95": None}
        ordered = sorted(values)
        p95_idx = max(0, int(round(0.95 * (len(ordered) - 1))))
        return {
            "count": len(values),
            "mean": round(statistics.fmean(values), 3),
            "median": round(statistics.median(values), 3),
            "p95": round(ordered[p95_idx], 3),
        }

    report: dict[str, Any] = {
        "analysis_type": "public_domain_shift",
        "evidence_class": "public_dataset_not_physical_pilot",
        "physical_pilot_data": False,
        "generalization_evidence_pass": False,
        "groups": {},
    }
    for tech in ("LTE", "5G"):
        group = bucket(tech)
        latencies = [float(r["latency_ms"]) for r in group if r.get("latency_ms") is not None]
        downloads = [float(r["download_kbps"]) for r in group if r.get("download_kbps") is not None]
        report["groups"][tech] = {
            "latency_ms": stats(latencies),
            "download_kbps": stats(downloads),
        }
    return report


def write_normalized_output(path: Path, normalized: NormalizedRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_id": normalized.source_id,
        "metadata": normalized.metadata,
        "records": list(normalized.records),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
