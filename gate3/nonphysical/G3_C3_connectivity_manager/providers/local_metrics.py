"""Local device/network metrics without operator APIs."""
from __future__ import annotations

from typing import Any, Dict

from .base import CapabilityMode, NetworkCapability, NetworkCapabilityProvider, ProviderUnavailableError


class LocalMetricsProvider(NetworkCapabilityProvider):
    provider_id = "local_metrics"

    def __init__(self, metrics: Dict[str, Any] | None = None, enabled: bool = True) -> None:
        self._enabled = enabled
        self._metrics = metrics or {
            "rtt_ms": 24.0,
            "loss_pct": 0.1,
            "bearer": "wifi",
            "connected_network_type": "WIFI",
        }

    def mode(self) -> CapabilityMode:
        return CapabilityMode.SIMULATED if self._enabled else CapabilityMode.UNAVAILABLE

    def list_capabilities(self) -> list[str]:
        if not self._enabled:
            return []
        return ["Connected Network Type", "Connectivity Insights"]

    def get_capability(self, name: str) -> NetworkCapability:
        if not self._enabled:
            raise ProviderUnavailableError("LocalMetricsProvider disabled")
        if name not in self.list_capabilities():
            raise ProviderUnavailableError(f"capability unavailable: {name}")
        return NetworkCapability(
            name=name,
            available=True,
            mode=CapabilityMode.SIMULATED,
            payload=dict(self._metrics),
            evidence_class="SOFTWARE",
        )
