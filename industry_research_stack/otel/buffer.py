"""Local-first offline telemetry buffer (OTLP-shaped, no network required)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping
import time

from .redaction import redact_attributes


@dataclass
class OfflineBuffer:
    max_events: int = 1000
    events: List[Dict[str, Any]] = field(default_factory=list)

    def emit(self, name: str, attributes: Mapping[str, Any] | None = None) -> dict:
        event = {
            "name": name,
            "ts": time.time(),
            "attributes": redact_attributes(attributes or {}),
            "export": "local_buffer",
        }
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events :]
        return event

    def flush(self) -> list[dict]:
        out = list(self.events)
        self.events.clear()
        return out

    def snapshot(self) -> list[dict]:
        return list(self.events)
