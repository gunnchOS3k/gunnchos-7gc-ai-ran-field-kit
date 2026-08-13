"""Connectivity manager with NTN abstraction and NetworkCapabilityProvider.

PHYSICAL_EXECUTION_FREEZE ACTIVE — no real NTN or operator claim without credentials.
STANDARDIZED_6G=false. CARRIER_ACCEPTED=false. RM520N-GL is not NTN.
Ethernet is WAN. BLE is local/PAN, not WAN failover.
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

BEARERS = ("ethernet", "wifi", "cellular", "ble", "ntn_abstracted")
WAN_BEARERS = ("ethernet", "wifi", "cellular", "ntn_abstracted")

STANDARDIZED_6G = False
CARRIER_ACCEPTED = False


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
        default_factory=lambda: ["ethernet", "wifi", "cellular", "ntn_abstracted"]
    )
    capability_provider: Optional[NetworkCapabilityProvider] = None
    airplane: bool = False
    last_wan: Optional[str] = None
    reconnect_count: int = 0

    def set_link(self, bearer: str, up: bool, rtt_ms: Optional[float] = None) -> None:
        if bearer not in BEARERS:
            raise ValueError(f"unknown bearer {bearer}")
        if self.airplane and bearer != "ble":
            up = False
        self.links = [l for l in self.links if l.bearer != bearer]
        self.links.append(LinkState(bearer, up, rtt_ms))

    def select(self) -> Optional[LinkState]:
        if self.airplane:
            return None  # WAN offline; BLE is PAN-only and not returned as WAN
        by = {l.bearer: l for l in self.links if l.up}
        for b in self.preferred:
            if b in by:
                chosen = by[b]
                if chosen.bearer in WAN_BEARERS:
                    self.last_wan = chosen.bearer
                return chosen
        return None

    def set_airplane(self, enabled: bool) -> dict:
        self.airplane = bool(enabled)
        if self.airplane:
            for link in self.links:
                if link.bearer != "ble":
                    link.up = False
        return {
            "airplane": self.airplane,
            "active": None if self.airplane else (self.select().bearer if self.select() else None),
            "STANDARDIZED_6G": STANDARDIZED_6G,
            "CARRIER_ACCEPTED": CARRIER_ACCEPTED,
        }

    def failover(self, drop: str) -> dict:
        self.set_link(drop, False)
        chosen = self.select()
        return {
            "from": drop,
            "to": chosen.bearer if chosen else None,
            "offline": chosen is None,
            "STANDARDIZED_6G": STANDARDIZED_6G,
            "CARRIER_ACCEPTED": CARRIER_ACCEPTED,
            "real_ntn_claim": False,
        }

    def reconnect(self) -> dict:
        self.reconnect_count += 1
        if self.airplane:
            return {
                "ok": False,
                "reason": "airplane",
                "reconnect_count": self.reconnect_count,
                "CARRIER_ACCEPTED": CARRIER_ACCEPTED,
            }
        chosen = self.select()
        if chosen is None and self.last_wan:
            # last_wan remains a hint; caller must restore link liveness
            pass
        return {
            "ok": chosen is not None,
            "active": chosen.bearer if chosen else None,
            "last_wan": self.last_wan,
            "reconnect_count": self.reconnect_count,
            "STANDARDIZED_6G": STANDARDIZED_6G,
            "CARRIER_ACCEPTED": CARRIER_ACCEPTED,
        }

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
            "note": "NTN path is an interface stub; no satellite session claimed; not RM520N-GL",
            "network_capability": provider_claim,
            "real_operator_claim": bool(provider_claim.get("real_operator_claim")),
            "STANDARDIZED_6G": STANDARDIZED_6G,
            "CARRIER_ACCEPTED": CARRIER_ACCEPTED,
            "RM520N_GL_NTN": False,
            "ble_is_wan": False,
            "airplane": self.airplane,
        }
