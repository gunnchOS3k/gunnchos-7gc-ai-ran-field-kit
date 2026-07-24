"""Open-dataset adapter stub — refuses unverified licenses.

GENERALIZATION_EVIDENCE_PASS: NOT CLAIMED.
"""

from __future__ import annotations

from typing import Any, Mapping

from generalization.adapters.base import (
    EvidenceAdapter,
    EvidenceSource,
    LicenseVerificationError,
    NormalizedRecord,
)


class OpenDatasetAdapterStub(EvidenceAdapter):
    """Placeholder for open dataset ingest after manual license verification."""

    def __init__(self, source: EvidenceSource) -> None:
        super().__init__(source)
        if source.license_status != source.license_status.VERIFIED_LICENSE:
            # Fail fast at construction for unverified registry entries
            raise LicenseVerificationError(
                f"OpenDatasetAdapterStub cannot be constructed for "
                f"{source.id!r} with license_status "
                f"{source.license_status.value}."
            )

    def load(self) -> NormalizedRecord:
        self.assert_license_verified()
        # Execution path reserved for future verified sources only.
        raise NotImplementedError(
            f"Verified load not implemented for {self.source.id!r}; "
            "populate after license review and registry update."
        )

    def describe(self) -> Mapping[str, Any]:
        return {
            "adapter": "OpenDatasetAdapterStub",
            "source_id": self.source.id,
            "license_status": self.source.license_status.value,
            "status": "stub",
            "generalization_evidence_pass": False,
        }


def try_create_open_adapter(source: EvidenceSource) -> EvidenceAdapter:
    """Return adapter only for VERIFIED_LICENSE open_dataset_candidate sources."""
    if source.type != "open_dataset_candidate":
        raise LicenseVerificationError(
            f"Refusing open dataset adapter for {source.id!r}: "
            f"type={source.type!r} is not open_dataset_candidate."
        )
    if source.license_status != source.license_status.VERIFIED_LICENSE:
        raise LicenseVerificationError(
            f"Refusing open dataset adapter for {source.id!r}: "
            f"license_status={source.license_status.value}"
        )
    return OpenDatasetAdapterStub(source)
