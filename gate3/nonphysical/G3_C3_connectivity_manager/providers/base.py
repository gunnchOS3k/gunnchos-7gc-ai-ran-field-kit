"""NetworkCapabilityProvider abstraction.

Modes: UNAVAILABLE / SIMULATED / SANDBOX / REAL_OPERATOR.
REAL_OPERATOR must never be claimed without credentials.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional


class CapabilityMode(str, Enum):
    UNAVAILABLE = "UNAVAILABLE"
    SIMULATED = "SIMULATED"
    SANDBOX = "SANDBOX"
    REAL_OPERATOR = "REAL_OPERATOR"


class NetworkCapabilityError(Exception):
    """Base provider error."""


class ProviderUnavailableError(NetworkCapabilityError):
    """Provider or capability is unavailable."""


class ProviderFailureError(NetworkCapabilityError):
    """Transient or unexpected provider failure."""


class RateLimitError(NetworkCapabilityError):
    """Provider rate limit exceeded."""


class AuthExpiredError(NetworkCapabilityError):
    """Credentials expired or invalid."""


@dataclass(frozen=True)
class NetworkCapability:
    name: str
    available: bool
    mode: CapabilityMode
    payload: Mapping[str, Any] = field(default_factory=dict)
    evidence_class: str = "SIMULATED"


class NetworkCapabilityProvider(ABC):
    """Optional network capability source for connectivity manager."""

    provider_id: str = "base"

    @abstractmethod
    def mode(self) -> CapabilityMode:
        ...

    @abstractmethod
    def list_capabilities(self) -> list[str]:
        ...

    @abstractmethod
    def get_capability(self, name: str) -> NetworkCapability:
        ...

    def claim_boundary(self) -> Dict[str, Any]:
        m = self.mode()
        return {
            "provider_id": self.provider_id,
            "mode": m.value,
            "real_operator_claim": m == CapabilityMode.REAL_OPERATOR,
            "note": "REAL_OPERATOR requires verified credentials; never implied by presence of adapter code.",
        }
