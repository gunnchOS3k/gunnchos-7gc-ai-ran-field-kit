"""gunnchos.* OpenTelemetry semantic conventions namespace.

No PII by default. Grafana OSS is TEST_ONLY standalone — exporters stay replaceable.
"""
from __future__ import annotations

namespace_prefix = "gunnchos"

SEMANTIC_CONVENTIONS = {
    "device": {
        "gunnchos.device.id": "opaque device id (non-PII)",
        "gunnchos.device.role": "student_14_5|handheld_hybrid|ds_xl_coder|edge_io_rings",
        "gunnchos.device.firmware_version": "development image version",
    },
    "fleet": {
        "gunnchos.fleet.event_kind": "health|update|repair|telemetry",
        "gunnchos.fleet.device_count": "count of observed devices",
    },
    "network": {
        "gunnchos.network.bearer": "wifi|cellular|ble|ntn_abstracted",
        "gunnchos.network.capability_mode": "UNAVAILABLE|SIMULATED|SANDBOX|REAL_OPERATOR",
        "gunnchos.network.handoff_ms": "bearer handoff duration",
    },
    "ai_runtime": {
        "gunnchos.ai.model_id": "local model identifier",
        "gunnchos.ai.inference_ms": "inference latency",
    },
    "game": {
        "gunnchos.game.id": "beatlink-party|archive-of-life-artifact-world|pedestrian-pursuit|anime-aggressors",
        "gunnchos.game.fps": "frames per second",
        "gunnchos.game.frame_time_ms": "frame time",
        "gunnchos.game.input_latency_ms": "input-to-action latency",
        "gunnchos.game.core_loop_step": "instrumented core-loop step",
    },
    "update_recovery": {
        "gunnchos.update.stage": "download|verify|apply|rollback",
        "gunnchos.update.result": "ok|fail|tamper_detected",
    },
    "ring_input": {
        "gunnchos.ring.gesture": "gesture class label",
        "gunnchos.ring.confidence": "0..1 confidence",
        "gunnchos.ring.pipeline_ms": "pipeline latency",
    },
    "evidence": {
        "gunnchos.evidence.class": "SOFTWARE|SIMULATED|EXTERNAL|PHYSICAL_PENDING",
        "gunnchos.evidence.orchestration_id": "test/evidence run id",
    },
}

# Attributes that must never be exported by default
FORBIDDEN_DEFAULT_ATTRIBUTES = {
    "user.email",
    "user.name",
    "student.id",
    "student.name",
    "person.name",
    "phone.number",
    "ssn",
    "password",
    "auth.token",
}

GRAFANA_NOTE = (
    "Grafana OSS = TEST_ONLY standalone development observability backend (AGPLv3). "
    "Do not embed Grafana source. Keep OTel exporters/backends replaceable."
)
