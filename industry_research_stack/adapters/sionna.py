"""sionna adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class SionnaAdapter(ToolAdapter):
    tool_id = "sionna"
    license = "Apache-2.0"
    source_url = "https://github.com/NVlabs/sionna"
    pinned_version = "fixture-0.1.0"

    def detect(self) -> bool:
        return False  # GPU/Sionna optional; Tier-0 never requires it

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "channel": "tdl_a",
            "snr_db": 12.5,
            "bler": 0.02,
            "gpu_required": False,
            "note": "deterministic fixture channel result",
        }
