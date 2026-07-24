"""Tests for NordicDat public dataset adapter."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generalization.adapters.base import (  # noqa: E402
    LicenseStatus,
    LicenseVerificationError,
    resolve_source,
)
from generalization.adapters.nordicdat.adapter import (  # noqa: E402
    NordicDatAdapter,
    load_config,
    normalize_csv_rows,
    summarize_domain_shift,
)
from generalization.adapters.base import EvidenceSource, load_registry  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "nordicdat_sample.csv"
REGISTRY = ROOT / "generalization/EVIDENCE_SOURCE_REGISTRY.yaml"


class TestNordicDatAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config()

    def _verified_source(self) -> EvidenceSource:
        registry = load_registry(REGISTRY)
        return resolve_source(registry, "nordicdat_qos_public")

    def test_refuses_unverified_license(self) -> None:
        src = EvidenceSource(
            id="nordicdat_qos_public",
            type="open_dataset",
            status="BLOCKED",
            license_status=LicenseStatus.UNVERIFIED,
        )
        with self.assertRaises(LicenseVerificationError):
            NordicDatAdapter(src, config=self.config, csv_path=FIXTURE)

    def test_normalize_drops_missing_required(self) -> None:
        import csv

        with FIXTURE.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        normalized = normalize_csv_rows(rows, self.config)
        self.assertEqual(len(normalized), 3)
        self.assertNotIn("latitude", normalized[0])
        self.assertEqual(normalized[0]["access_technology"], "LTE")

    def test_load_fixture(self) -> None:
        adapter = NordicDatAdapter(
            self._verified_source(),
            config=self.config,
            csv_path=FIXTURE,
        )
        result = adapter.load()
        self.assertEqual(result.source_id, "nordicdat_qos_public")
        self.assertFalse(result.metadata["physical_pilot_data"])
        self.assertFalse(result.metadata["generalization_evidence_pass"])
        self.assertEqual(result.metadata["row_count_normalized"], 3)

    def test_describe_labels_public_evidence(self) -> None:
        adapter = NordicDatAdapter(
            self._verified_source(),
            config=self.config,
            csv_path=FIXTURE,
        )
        meta = adapter.describe()
        self.assertFalse(meta["physical_pilot_data"])
        self.assertFalse(meta["generalization_evidence_pass"])

    def test_domain_shift_summary(self) -> None:
        import csv

        with FIXTURE.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        records = normalize_csv_rows(rows, self.config)
        report = summarize_domain_shift(records)
        self.assertFalse(report["generalization_evidence_pass"])
        self.assertIn("LTE", report["groups"])
        self.assertIn("5G", report["groups"])
        self.assertEqual(report["groups"]["LTE"]["latency_ms"]["count"], 2)

    def test_config_has_verified_license(self) -> None:
        self.assertEqual(self.config["license"]["verification_status"], "VERIFIED_LICENSE")
        self.assertIn("CC BY 4.0", self.config["license"]["name"])


if __name__ == "__main__":
    unittest.main()
