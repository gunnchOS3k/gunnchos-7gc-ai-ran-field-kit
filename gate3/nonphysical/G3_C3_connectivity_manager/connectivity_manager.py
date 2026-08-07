"""Connectivity manager with NTN abstraction — no real NTN claim."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

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
    preferred: List[str] = field(default_factory=lambda: ["wifi", "cellular", "ntn_abstracted", "ble"])

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

    def claim_boundary(self) -> dict:
        return {
            "ntn": "ABSTRACTED_ONLY",
            "real_ntn_claim": False,
            "evidence_class": "SIMULATED",
            "note": "NTN path is an interface stub; no satellite session claimed",
        }
