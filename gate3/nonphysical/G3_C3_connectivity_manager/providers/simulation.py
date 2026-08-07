"""Deterministic simulation provider for CI / Tier-0 paths."""
from __future__ import annotations

from .base import (
    CapabilityMode,
    NetworkCapability,
    NetworkCapabilityProvider,
    ProviderFailureError,
    ProviderUnavailableError,
)


class SimulationProvider(NetworkCapabilityProvider):
    provider_id = "simulation"

    CAPABILITIES = {
        "Connectivity Insights": {"qos_hint": "best_effort", "confidence": 0.9},
        "Connected Network Type": {"type": "CELLULAR", "generation": "5G"},
        "Simple Edge Discovery": {"edge_id": "sim-edge-1", "latency_ms": 12},
        "Application Profiles": {"profile": "interactive_gaming"},
        "Quality on Demand": {"supported": False, "reason": "not_in_fixture"},
    }

    def __init__(self, fail_next: bool = False, unavailable: bool = False) -> None:
        self._fail_next = fail_next
        self._unavailable = unavailable

    def mode(self) -> CapabilityMode:
        return CapabilityMode.UNAVAILABLE if self._unavailable else CapabilityMode.SIMULATED

    def list_capabilities(self) -> list[str]:
        if self._unavailable:
            return []
        return list(self.CAPABILITIES)

    def get_capability(self, name: str) -> NetworkCapability:
        if self._unavailable:
            raise ProviderUnavailableError("SimulationProvider unavailable")
        if self._fail_next:
            self._fail_next = False
            raise ProviderFailureError("simulated provider failure")
        if name not in self.CAPABILITIES:
            raise ProviderUnavailableError(f"unknown capability: {name}")
        return NetworkCapability(
            name=name,
            available=True,
            mode=CapabilityMode.SIMULATED,
            payload=dict(self.CAPABILITIES[name]),
            evidence_class="SIMULATED",
        )
