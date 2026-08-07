"""CAMARA real-operator provider — credentials required for REAL_OPERATOR."""
from __future__ import annotations

from .base import (
    AuthExpiredError,
    CapabilityMode,
    NetworkCapability,
    NetworkCapabilityProvider,
    ProviderUnavailableError,
    RateLimitError,
)


class CAMARARealProvider(NetworkCapabilityProvider):
    provider_id = "camara_real"

    def __init__(
        self,
        *,
        credentials: dict | None = None,
        rate_limited: bool = False,
        auth_expired: bool = False,
    ) -> None:
        self._credentials = credentials
        self._rate_limited = rate_limited
        self._auth_expired = auth_expired

    def _has_credentials(self) -> bool:
        if not self._credentials:
            return False
        return bool(self._credentials.get("client_id") and self._credentials.get("client_secret"))

    def mode(self) -> CapabilityMode:
        if not self._has_credentials():
            return CapabilityMode.UNAVAILABLE
        return CapabilityMode.REAL_OPERATOR

    def list_capabilities(self) -> list[str]:
        if self.mode() != CapabilityMode.REAL_OPERATOR:
            return []
        return [
            "Connectivity Insights",
            "Connected Network Type",
            "Simple Edge Discovery",
            "Application Profiles",
            "Quality on Demand",
        ]

    def get_capability(self, name: str) -> NetworkCapability:
        if not self._has_credentials():
            raise ProviderUnavailableError(
                "CAMARARealProvider has no credentials; mode=UNAVAILABLE (no REAL claim)"
            )
        if self._auth_expired:
            raise AuthExpiredError("operator credentials expired")
        if self._rate_limited:
            raise RateLimitError("operator API rate limit exceeded")
        if name not in self.list_capabilities():
            raise ProviderUnavailableError(f"operator capability unavailable: {name}")
        return NetworkCapability(
            name=name,
            available=True,
            mode=CapabilityMode.REAL_OPERATOR,
            payload={
                "operator": self._credentials.get("operator", "unknown"),
                "capability": name,
                "credentials_present": True,
            },
            evidence_class="EXTERNAL_OPERATOR",
        )

    def claim_boundary(self) -> dict:
        m = self.mode()
        return {
            "provider_id": self.provider_id,
            "mode": m.value,
            "real_operator_claim": m == CapabilityMode.REAL_OPERATOR,
            "credentials_present": self._has_credentials(),
            "note": "REAL_OPERATOR only when credentials present; otherwise UNAVAILABLE.",
        }
