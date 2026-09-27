"""Safe RIC adapter layer. No real E2 claim."""
from __future__ import annotations

from typing import Any, Protocol

from .actuation_firewall import evaluate_request, real_actuation_enabled


class RICAdapter(Protocol):
    name: str

    def read_telemetry(self, site_id: str) -> dict[str, Any]: ...

    def recommend(self, context: dict[str, Any]) -> dict[str, Any]: ...

    def actuate(self, request: dict[str, Any]) -> dict[str, Any]: ...


class SimulatedRICAdapter:
    name = "simulated"

    def read_telemetry(self, site_id: str) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "site_id": site_id,
            "mode": "simulated",
            "e2_claimed": False,
            "samples": [
                {"metric": "rsrp_dbm", "value": -85.0, "origin": "simulated"},
                {"metric": "latency_ms", "value": 24.0, "origin": "simulated"},
            ],
        }

    def recommend(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": "recommendation_only",
            "would_have_applied": False,
            "context_site": context.get("site_id"),
            "e2_claimed": False,
        }

    def actuate(self, request: dict[str, Any]) -> dict[str, Any]:
        receipt = evaluate_request(request)
        receipt["reason"] = "SimulatedRICAdapter never applies physical control"
        receipt["applied"] = False
        if receipt["decision"] == "applied_testbed":
            receipt["decision"] = "shadow_recorded"
        return receipt


class ReadOnlyTelemetryAdapter:
    name = "read_only_telemetry"

    def read_telemetry(self, site_id: str) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "site_id": site_id,
            "mode": "read_only",
            "e2_claimed": False,
            "samples": [],
        }

    def recommend(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": "recommendation_only",
            "site_id": context.get("site_id"),
            "e2_claimed": False,
        }

    def actuate(self, request: dict[str, Any]) -> dict[str, Any]:
        receipt = evaluate_request(request)
        receipt["decision"] = "denied"
        receipt["applied"] = False
        receipt["reason"] = "ReadOnlyTelemetryAdapter refuses actuation"
        return receipt


class MockTestbedRICAdapter:
    name = "mock_testbed"

    def read_telemetry(self, site_id: str) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "site_id": site_id,
            "mode": "mock_testbed",
            "e2_claimed": False,
            "authorized_testbed_control": False,
        }

    def recommend(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": "shadow",
            "site_id": context.get("site_id"),
            "e2_claimed": False,
        }

    def actuate(self, request: dict[str, Any]) -> dict[str, Any]:
        receipt = evaluate_request(request)
        if real_actuation_enabled():
            receipt["decision"] = "shadow_recorded"
            receipt["reason"] = "mock testbed records shadow only; no E2"
        receipt["applied"] = False
        receipt["e2_claimed"] = False
        return receipt


class _FailClosedOptionalBackend:
    def __init__(self, name: str) -> None:
        self.name = name

    def read_telemetry(self, site_id: str) -> dict[str, Any]:
        raise RuntimeError(f"{self.name} backend is optional and fail-closed")

    def recommend(self, context: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError(f"{self.name} backend is optional and fail-closed")

    def actuate(self, request: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError(
            f"{self.name} backend is optional and fail-closed; no E2 claim"
        )


class SrsRANAdapter(_FailClosedOptionalBackend):
    def __init__(self) -> None:
        super().__init__("srsRAN")


class OAIAdapter(_FailClosedOptionalBackend):
    def __init__(self) -> None:
        super().__init__("OAI")


class ORANSCAdapter(_FailClosedOptionalBackend):
    def __init__(self) -> None:
        super().__init__("O-RAN-SC")


ADAPTERS = {
    "simulated": SimulatedRICAdapter,
    "read_only_telemetry": ReadOnlyTelemetryAdapter,
    "mock_testbed": MockTestbedRICAdapter,
    "srsran": SrsRANAdapter,
    "oai": OAIAdapter,
    "oran_sc": ORANSCAdapter,
}
