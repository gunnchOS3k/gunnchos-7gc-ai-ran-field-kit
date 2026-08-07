"""Shared adapter contract for industry research tools.

Tier 0 fixtures always pass without GPU/external tools.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional
import json


@dataclass(frozen=True)
class AdapterResult:
    tool_id: str
    mode: str  # FIXTURE | DETECTED | EXTERNAL | UNAVAILABLE
    license: str
    version: str
    source_url: str
    provenance: Mapping[str, Any]
    payload: Mapping[str, Any] = field(default_factory=dict)
    available: bool = True

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "mode": self.mode,
            "license": self.license,
            "version": self.version,
            "source_url": self.source_url,
            "provenance": dict(self.provenance),
            "payload": dict(self.payload),
            "available": self.available,
        }


class ToolAdapter(ABC):
    tool_id: str
    license: str
    source_url: str
    pinned_version: str

    @abstractmethod
    def detect(self) -> bool:
        """Return True if real tool appears available."""

    @abstractmethod
    def fixture_payload(self) -> Mapping[str, Any]:
        ...

    def run(self, prefer_real: bool = False) -> AdapterResult:
        detected = self.detect()
        if prefer_real and detected:
            mode = "DETECTED"
            payload = dict(self.fixture_payload())
            payload["note"] = "detected_local_tool; using fixture-equivalent output under freeze"
        else:
            mode = "FIXTURE"
            payload = dict(self.fixture_payload())
        return AdapterResult(
            tool_id=self.tool_id,
            mode=mode,
            license=self.license,
            version=self.pinned_version,
            source_url=self.source_url,
            provenance={
                "tier": 0 if mode == "FIXTURE" else 1,
                "physical_execution_freeze": "ACTIVE",
                "detection": detected,
                "false_claim_guard": True,
            },
            payload=payload,
            available=True,
        )


def detect_or_fixture(adapter: ToolAdapter, prefer_real: bool = False) -> AdapterResult:
    return adapter.run(prefer_real=prefer_real)


def write_fixture(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
