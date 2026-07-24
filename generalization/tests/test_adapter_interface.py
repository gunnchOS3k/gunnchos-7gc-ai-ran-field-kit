"""Tests for generalization adapter interface."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "generalization").is_dir():
    ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generalization.adapters.base import (  # noqa: E402
    EvidenceSource,
    LicenseStatus,
    LicenseVerificationError,
    resolve_source,
)
from generalization.adapters.open_dataset_stub import (  # noqa: E402
    OpenDatasetAdapterStub,
    try_create_open_adapter,
)


REGISTRY_FIXTURE = {
    "sources": [
        {
            "id": "open_mlab_stub",
            "type": "open_dataset_candidate",
            "status": "BLOCKED",
            "license_status": "UNVERIFIED",
            "uri": "https://www.measurementlab.net/",
        },
        {
            "id": "verified_example",
            "type": "open_dataset_candidate",
            "status": "AUTOMATION_READY",
            "license_status": "VERIFIED_LICENSE",
            "uri": "https://example.com/dataset",
        },
        {
            "id": "gary_pilot_local",
            "type": "physical_pilot",
            "status": "HUMAN_ACTION_REQUIRED",
            "license_status": "INTERNAL_CONSENT_GATED",
        },
    ]
}


class TestEvidenceSource(unittest.TestCase):
    def test_from_mapping(self) -> None:
        src = EvidenceSource.from_mapping(REGISTRY_FIXTURE["sources"][0])
        self.assertEqual(src.id, "open_mlab_stub")
        self.assertEqual(src.license_status, LicenseStatus.UNVERIFIED)

    def test_resolve_source(self) -> None:
        src = resolve_source(REGISTRY_FIXTURE, "verified_example")
        self.assertEqual(src.license_status, LicenseStatus.VERIFIED_LICENSE)


class TestOpenDatasetAdapterStub(unittest.TestCase):
    def test_refuses_unverified_at_construction(self) -> None:
        src = resolve_source(REGISTRY_FIXTURE, "open_mlab_stub")
        with self.assertRaises(LicenseVerificationError):
            OpenDatasetAdapterStub(src)

    def test_try_create_refuses_unverified(self) -> None:
        src = resolve_source(REGISTRY_FIXTURE, "open_mlab_stub")
        with self.assertRaises(LicenseVerificationError):
            try_create_open_adapter(src)

    def test_verified_constructs_but_load_not_implemented(self) -> None:
        src = resolve_source(REGISTRY_FIXTURE, "verified_example")
        adapter = OpenDatasetAdapterStub(src)
        self.assertEqual(adapter.describe()["generalization_evidence_pass"], False)
        with self.assertRaises(NotImplementedError):
            adapter.load()

    def test_internal_consent_gated_refused_for_open_adapter(self) -> None:
        src = resolve_source(REGISTRY_FIXTURE, "gary_pilot_local")
        with self.assertRaises(LicenseVerificationError):
            try_create_open_adapter(src)


if __name__ == "__main__":
    unittest.main()
