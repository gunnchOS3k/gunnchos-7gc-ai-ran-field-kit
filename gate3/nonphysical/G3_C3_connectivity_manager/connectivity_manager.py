"""Connectivity manager with NTN abstraction and NetworkCapabilityProvider.

PHYSICAL_EXECUTION_FREEZE ACTIVE — no real NTN or operator claim without credentials.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .providers.base import (
    CapabilityMode,
    NetworkCapability,
    NetworkCapabilityError,
    NetworkCapabilityProvider,
)

BEARERS = ("wifi", "cellular", "ble", "ntn_abstracted")


@dataclass
class LinkState:
    bearer: str
    up: bool
    rtt_ms: Optional[float] = None
    evidence_class: str = "SIMULATED"


@dataclass
class ConnectivityManager:
    links: List[LinkState] = field(default_factory=list)
    preferred: List[str] = field(
        default_factory=lambda: ["wifi", "cellular", "ntn_abstracted", "ble"]
    )
    capability_provider: Optional[NetworkCapabilityProvider] = None

    def set_link(self, bearer: str, up: bool, rtt_ms: Optional[float] = None) -> None:
        if bearer not in BEARERS:
            raise ValueError(f"unknown bearer {bearer}")
        self.links = [l for l in self.links if l.bearer != bearer]
        self.links.append(LinkState(bearer, up, rtt_ms))

    def select(self) -> Optional[LinkState]:
        by = {l.bearer: l for l in self.links if l.up}
        for b in self.preferred:
            if b in by:
                return by[b]
        return None

    def capability_mode(self) -> CapabilityMode:
        if self.capability_provider is None:
            return CapabilityMode.UNAVAILABLE
        return self.capability_provider.mode()

    def get_network_capability(self, name: str) -> NetworkCapability:
        if self.capability_provider is None:
            raise NetworkCapabilityError("no capability provider configured")
        return self.capability_provider.get_capability(name)

    def claim_boundary(self) -> dict:
        provider_claim = (
            self.capability_provider.claim_boundary()
            if self.capability_provider is not None
            else {
                "provider_id": None,
                "mode": CapabilityMode.UNAVAILABLE.value,
                "real_operator_claim": False,
            }
        )
        return {
            "ntn": "ABSTRACTED_ONLY",
            "real_ntn_claim": False,
            "evidence_class": "SIMULATED",
            "note": "NTN path is an interface stub; no satellite session claimed",
            "network_capability": provider_claim,
            "real_operator_claim": bool(provider_claim.get("real_operator_claim")),
        }
