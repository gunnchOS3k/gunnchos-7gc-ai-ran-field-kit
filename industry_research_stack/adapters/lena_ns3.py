"""lena_ns3 adapter — Tier-0 fixture always available."""
from __future__ import annotations

from typing import Any, Mapping

from .base import ToolAdapter


class LenaNs3Adapter(ToolAdapter):
    tool_id = "lena_ns3"
    license = "GPL-2.0"
    source_url = "https://cttc-lena.gitlab.io/5g-lena-website/"
    pinned_version = "external-runner-0.1.0"

    def detect(self) -> bool:
        return False  # external ns-3/5G-LENA process only

    def fixture_payload(self) -> Mapping[str, Any]:
        return {
            "runner": "external",
            "scenario": "nr_simple",
            "throughput_mbps": 42.0,
            "linked_into_product": False,
            "note": "GPL external-runner boundary; no in-process link",
        }
