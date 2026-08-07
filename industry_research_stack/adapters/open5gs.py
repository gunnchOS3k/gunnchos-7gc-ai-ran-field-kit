"""open5gs adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class Open5gsAdapter(ToolAdapter):
    tool_id = "open5gs"
    license = "AGPL-3.0"
    source_url = "https://open5gs.org/"
    pinned_version = "external-testbed-0.1.0"

    def detect(self) -> bool:
        return False

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "deployment": "standalone_container",
            "embedded_in_product": False,
            "note": "AGPL standalone lab fixture",
        }
