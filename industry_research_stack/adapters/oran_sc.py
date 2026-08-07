"""oran_sc adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class OranScAdapter(ToolAdapter):
    tool_id = "oran_sc"
    license = "Apache-2.0"
    source_url = "https://o-ran-sc.org/about/"
    pinned_version = "refs-fixture-0.1.0"

    def detect(self) -> bool:
        return False

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "components": ["near-rt-ric", "o1", "a1"],
            "mode": "reference",
            "note": "O-RAN SC interface/test references only",
        }
