"""Probe backend adapters. Missing backends FAIL CLOSED — never fake AODT/pyAerial/Sionna."""
from __future__ import annotations

import importlib.util
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


BACKENDS = (
    ("SIONNA_PHY", "sionna"),
    ("SIONNA_SYS", "sionna"),
    ("SIONNA_RT", "sionna"),
    ("AODT", "aodt"),
    ("PYAERIAL", "pyaerial"),
    ("AERIAL_SDK", "aerial"),
    ("AERIAL_CUDA_RAN", "aerial"),
)


@dataclass
class AdapterReport:
    backend_id: str
    import_module: str
    present: bool
    status: str
    silent_fake_forbidden: bool = True
    error: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _available(module: str) -> tuple[bool, str | None]:
    if importlib.util.find_spec(module) is None:
        return False, f"ModuleNotFoundError: No module named '{module}'"
    try:
        __import__(module)
        return True, None
    except Exception as exc:  # pragma: no cover - import-time failures
        return False, f"{type(exc).__name__}: {exc}"


def probe_one(backend_id: str, module: str) -> AdapterReport:
    ok, err = _available(module)
    if ok:
        return AdapterReport(
            backend_id=backend_id,
            import_module=module,
            present=True,
            status="AVAILABLE",
            notes=["Real import succeeded; no stub substitution."],
        )
    return AdapterReport(
        backend_id=backend_id,
        import_module=module,
        present=False,
        status="UNAVAILABLE_FAIL_CLOSED",
        error=err,
        notes=[
            "FAIL CLOSED: do not fabricate AODT/pyAerial/Sionna results.",
            "CPU/NumPy analytical path remains allowed when declared explicitly.",
        ],
    )


def probe_all() -> dict[str, Any]:
    reports = [probe_one(bid, mod) for bid, mod in BACKENDS]
    any_gpuish = any(r.present for r in reports)
    return {
        "schema": "gunnchos.external_reproduction.adapter_probe.v1",
        "any_nvidia_or_sionna_backend_available": any_gpuish,
        "adapters": {r.backend_id: r.to_dict() for r in reports},
        "policy": {
            "silent_fake_aodt": False,
            "silent_fake_pyaerial": False,
            "silent_fake_sionna": False,
            "silent_fake_aerial": False,
            "cpu_numerical_allowed": True,
        },
    }


def write_probe(path: Path) -> dict[str, Any]:
    payload = probe_all()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
