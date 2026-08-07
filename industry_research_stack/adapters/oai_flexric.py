"""oai_flexric adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class OaiFlexricAdapter(ToolAdapter):
    tool_id = "oai_flexric"
    license = "OAI-CSSL"
    source_url = "https://openairinterface.org/"
    pinned_version = "research-fixture-0.1.0"

    def detect(self) -> bool:
        return False

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "ric": "flexric",
            "e2_sm": "KPM",
            "commercial_runtime_mandatory": False,
            "note": "research/lab interface fixture",
        }
