"""Base adapter interface for generalization evidence sources.

Adapters MUST refuse to load sources without VERIFIED_LICENSE in the registry.
GENERALIZATION_EVIDENCE_PASS is not claimed by this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence


class LicenseStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED_LICENSE = "VERIFIED_LICENSE"
    INTERNAL_CONSENT_GATED = "INTERNAL_CONSENT_GATED"
    PUBLIC_STANDARD = "PUBLIC_STANDARD"


class AdapterError(Exception):
    """Base error for adapter failures."""


class LicenseVerificationError(AdapterError):
    """Raised when license is not verified for ingest."""


class SourceNotFoundError(AdapterError):
    """Raised when registry source id is missing."""


@dataclass(frozen=True)
class EvidenceSource:
    id: str
    type: str
    status: str
    license_status: LicenseStatus
    uri: str | None = None
    notes: str | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> EvidenceSource:
        raw = data.get("license_status", "UNVERIFIED")
        try:
            license_status = LicenseStatus(str(raw))
        except ValueError as exc:
            raise AdapterError(f"Unknown license_status: {raw}") from exc
        return cls(
            id=str(data["id"]),
            type=str(data.get("type", "unknown")),
            status=str(data.get("status", "UNKNOWN")),
            license_status=license_status,
            uri=data.get("uri"),
            notes=data.get("notes"),
        )


@dataclass(frozen=True)
class NormalizedRecord:
    """Minimal normalized output — extend when VERIFIED sources exist."""

    source_id: str
    records: Sequence[Mapping[str, Any]]
    metadata: Mapping[str, Any]


class EvidenceAdapter(ABC):
    """Interface for external/generalization dataset adapters."""

    def __init__(self, source: EvidenceSource) -> None:
        self.source = source

    def assert_license_verified(self) -> None:
        if self.source.license_status != LicenseStatus.VERIFIED_LICENSE:
            raise LicenseVerificationError(
                f"Source {self.source.id!r} has license_status "
                f"{self.source.license_status.value}; ingest refused."
            )

    @abstractmethod
    def load(self) -> NormalizedRecord:
        """Load and normalize records. Must call assert_license_verified()."""

    @abstractmethod
    def describe(self) -> Mapping[str, Any]:
        """Return adapter metadata for audit logs."""


def resolve_source(
    registry: Mapping[str, Any], source_id: str
) -> EvidenceSource:
    sources = registry.get("sources", [])
    for entry in sources:
        if entry.get("id") == source_id:
            return EvidenceSource.from_mapping(entry)
    raise SourceNotFoundError(f"Source id not found in registry: {source_id}")


def load_registry(path: Path) -> Mapping[str, Any]:
    import yaml  # lazy import — optional dependency at runtime

    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
