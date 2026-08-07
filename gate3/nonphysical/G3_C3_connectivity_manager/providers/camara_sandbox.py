"""CAMARA sandbox provider — never REAL_OPERATOR."""
from __future__ import annotations

from .base import (
    AuthExpiredError,
    CapabilityMode,
    NetworkCapability,
    NetworkCapabilityProvider,
    ProviderUnavailableError,
    RateLimitError,
)


class CAMARASandboxProvider(NetworkCapabilityProvider):
    provider_id = "camara_sandbox"

    def __init__(
        self,
        *,
        enabled: bool = True,
        rate_limited: bool = False,
        auth_expired: bool = False,
        token: str | None = "sandbox-token",
    ) -> None:
        self._enabled = enabled
        self._rate_limited = rate_limited
        self._auth_expired = auth_expired
        self._token = token

    def mode(self) -> CapabilityMode:
        if not self._enabled or not self._token:
            return CapabilityMode.UNAVAILABLE
        return CapabilityMode.SANDBOX

    def list_capabilities(self) -> list[str]:
        if self.mode() == CapabilityMode.UNAVAILABLE:
            return []
        return [
            "Connectivity Insights",
            "Connected Network Type",
            "Simple Edge Discovery",
            "Application Profiles",
        ]

    def get_capability(self, name: str) -> NetworkCapability:
        if self.mode() == CapabilityMode.UNAVAILABLE:
            raise ProviderUnavailableError("CAMARA sandbox unavailable")
        if self._auth_expired:
            raise AuthExpiredError("sandbox auth expired")
        if self._rate_limited:
            raise RateLimitError("sandbox rate limit exceeded")
        if name not in self.list_capabilities():
            raise ProviderUnavailableError(f"sandbox capability unavailable: {name}")
        return NetworkCapability(
            name=name,
            available=True,
            mode=CapabilityMode.SANDBOX,
            payload={"sandbox": True, "capability": name, "operator_claim": False},
            evidence_class="SOFTWARE",
        )

    def claim_boundary(self) -> dict:
        base = super().claim_boundary()
        base["real_operator_claim"] = False
        base["note"] = "SANDBOX only; credentials are non-production sandbox tokens."
        return base
