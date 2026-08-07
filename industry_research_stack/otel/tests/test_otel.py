from industry_research_stack.otel import (
    InstrumentationHooks,
    OfflineBuffer,
    SEMANTIC_CONVENTIONS,
    namespace_prefix,
    redact_attributes,
)


def test_namespace_and_conventions():
    assert namespace_prefix == "gunnchos"
    assert "game" in SEMANTIC_CONVENTIONS
    assert "gunnchos.game.fps" in SEMANTIC_CONVENTIONS["game"]


def test_redaction_strips_pii_by_default():
    out = redact_attributes(
        {
            "gunnchos.game.fps": 60,
            "user.email": "a@b.com",
            "note": "contact student@school.edu or +1-555-0100",
        }
    )
    assert out["gunnchos.game.fps"] == 60
    assert out["user.email"] == "[REDACTED]"
    assert "[REDACTED_EMAIL]" in out["note"]
    assert "[REDACTED_PHONE]" in out["note"]


def test_offline_buffer_and_hooks():
    buf = OfflineBuffer(max_events=3)
    hooks = InstrumentationHooks(buf)
    hooks.game("frame", **{"gunnchos.game.fps": 58, "user.email": "x@y.com"})
    hooks.network("handoff", **{"gunnchos.network.bearer": "wifi"})
    assert len(buf.snapshot()) == 2
    assert buf.snapshot()[0]["attributes"]["user.email"] == "[REDACTED]"
    assert hooks.backend_policy()["grafana_oss"] == "TEST_ONLY"
    assert hooks.backend_policy()["pii_default"] is False
    flushed = buf.flush()
    assert len(flushed) == 2
    assert buf.snapshot() == []


def test_buffer_truncation():
    buf = OfflineBuffer(max_events=2)
    buf.emit("a", {})
    buf.emit("b", {})
    buf.emit("c", {})
    assert [e["name"] for e in buf.snapshot()] == ["b", "c"]
