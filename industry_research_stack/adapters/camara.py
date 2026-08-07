"""camara adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class CamaraAdapter(ToolAdapter):
    tool_id = "camara"
    license = "Apache-2.0 (API specs; operator terms apply)"
    source_url = "https://camaraproject.org/api-overview/"
    pinned_version = "adapter-0.1.0"

    def detect(self) -> bool:
        return False

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "modes": ["UNAVAILABLE", "SIMULATED", "SANDBOX", "REAL_OPERATOR"],
            "real_operator_without_credentials": False,
            "capabilities": [
                "Connectivity Insights",
                "Connected Network Type",
                "Simple Edge Discovery",
                "Application Profiles",
            ],
        }
