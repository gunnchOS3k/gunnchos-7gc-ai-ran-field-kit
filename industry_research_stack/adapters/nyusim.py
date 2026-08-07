"""nyusim adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class NyusimAdapter(ToolAdapter):
    tool_id = "nyusim"
    license = "Academic/NYU terms (verify per release)"
    source_url = "https://wireless.engineering.nyu.edu/nyusim-thz-mmwave-channel-simulator-research2/"
    pinned_version = "fixture-0.1.0"

    def detect(self) -> bool:
        return False

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "scenario": "UMi",
            "carrier_ghz": 28.0,
            "path_loss_db": 98.4,
            "note": "NYUSIM fixture path-loss sample",
        }
