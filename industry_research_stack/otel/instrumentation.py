"""Instrumentation hooks for device/fleet/network/game/AI/evidence."""
from __future__ import annotations

from typing import Any, Mapping, Optional

from .buffer import OfflineBuffer
from .conventions import GRAFANA_NOTE, namespace_prefix
from .redaction import redact_attributes


class InstrumentationHooks:
    def __init__(self, buffer: Optional[OfflineBuffer] = None) -> None:
        self.buffer = buffer or OfflineBuffer()

    def record(self, domain: str, name: str, **attrs: Any) -> dict:
        full = f"{namespace_prefix}.{domain}.{name}"
        return self.buffer.emit(full, redact_attributes(attrs))

    def device(self, name: str, **attrs: Any) -> dict:
        return self.record("device", name, **attrs)

    def fleet(self, name: str, **attrs: Any) -> dict:
        return self.record("fleet", name, **attrs)

    def network(self, name: str, **attrs: Any) -> dict:
        return self.record("network", name, **attrs)

    def ai(self, name: str, **attrs: Any) -> dict:
        return self.record("ai", name, **attrs)

    def game(self, name: str, **attrs: Any) -> dict:
        return self.record("game", name, **attrs)

    def update(self, name: str, **attrs: Any) -> dict:
        return self.record("update", name, **attrs)

    def ring(self, name: str, **attrs: Any) -> dict:
        return self.record("ring", name, **attrs)

    def evidence(self, name: str, **attrs: Any) -> dict:
        return self.record("evidence", name, **attrs)

    def backend_policy(self) -> Mapping[str, Any]:
        return {
            "primary": "opentelemetry",
            "grafana_oss": "TEST_ONLY",
            "note": GRAFANA_NOTE,
            "pii_default": False,
            "local_first": True,
        }
