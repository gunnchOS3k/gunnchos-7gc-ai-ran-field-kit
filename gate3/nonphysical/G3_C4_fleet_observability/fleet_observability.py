"""Fleet observability event bus (NONPHYSICAL)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import time

@dataclass
class FleetEvent:
    device_id: str
    kind: str
    payload: Dict[str, Any]
    ts: float = field(default_factory=time.time)
    evidence_class: str = "SOFTWARE"

@dataclass
class FleetObservability:
    events: List[FleetEvent] = field(default_factory=list)

    def emit(self, device_id: str, kind: str, **payload) -> FleetEvent:
        ev = FleetEvent(device_id, kind, payload)
        self.events.append(ev)
        return ev

    def query(self, kind: str | None = None) -> List[FleetEvent]:
        if kind is None:
            return list(self.events)
        return [e for e in self.events if e.kind == kind]

    def health_summary(self) -> dict:
        return {
            "devices": sorted({e.device_id for e in self.events}),
            "event_count": len(self.events),
            "evidence_class": "SOFTWARE",
        }
