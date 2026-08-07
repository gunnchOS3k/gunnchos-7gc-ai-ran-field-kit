"""Display/controls HAL with nonphysical backends + physical collector stubs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, List, Dict, Any

class DisplayBackend(Protocol):
    def draw_frame(self, framebuffer: bytes) -> None: ...
    def backend_kind(self) -> str: ...

class ControlsBackend(Protocol):
    def poll_events(self) -> List[Dict[str, Any]]: ...
    def backend_kind(self) -> str: ...

@dataclass
class EmulatorDisplay:
    frames: int = 0
    def draw_frame(self, framebuffer: bytes) -> None:
        self.frames += 1
    def backend_kind(self) -> str:
        return "NONPHYSICAL_EMULATOR"

@dataclass
class MockControls:
    queue: List[Dict[str, Any]] = field(default_factory=list)
    def poll_events(self) -> List[Dict[str, Any]]:
        events, self.queue = self.queue, []
        return events
    def backend_kind(self) -> str:
        return "NONPHYSICAL_MOCK"

@dataclass
class PhysicalCollectorStub:
    """Ready for later MEASURED capture; never fabricates measurements."""
    status: str = "PHYSICAL_PENDING"
    def collect(self) -> Dict[str, Any]:
        return {"evidence_class": "PHYSICAL_PENDING", "samples": [], "status": self.status}

@dataclass
class DisplayControlsHAL:
    display: DisplayBackend
    controls: ControlsBackend
    physical_collector: PhysicalCollectorStub = field(default_factory=PhysicalCollectorStub)

    def render(self, fb: bytes) -> None:
        self.display.draw_frame(fb)

    def events(self) -> List[Dict[str, Any]]:
        return self.controls.poll_events()

    def claim_label(self) -> str:
        return f"{self.display.backend_kind()}+{self.controls.backend_kind()}"
