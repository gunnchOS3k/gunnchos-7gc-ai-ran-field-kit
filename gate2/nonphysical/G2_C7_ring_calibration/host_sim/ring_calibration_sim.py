"""Ring pairing/calibration/drift/fallback host simulator."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math, time

@dataclass
class RingDevice:
    ring_id: str
    paired: bool = False
    calibrated: bool = False
    offset: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    drift_per_s: float = 0.01
    last_cal_ts: float = 0.0

@dataclass
class HostRingSimulator:
    rings: dict = field(default_factory=dict)
    fallback_mode: str = "none"  # none|gesture_disabled|host_controls

    def pair(self, ring_id: str) -> str:
        self.rings[ring_id] = RingDevice(ring_id, paired=True)
        return "PAIRED"

    def calibrate(self, ring_id: str, reference=(0.0, 0.0, 1.0)) -> str:
        r = self.rings[ring_id]
        if not r.paired:
            return "REJECT_NOT_PAIRED"
        r.offset = list(reference)
        r.calibrated = True
        r.last_cal_ts = time.time()
        self.fallback_mode = "none"
        return "CALIBRATED"

    def sample(self, ring_id: str, raw=(0.1, 0.0, 0.9), now: Optional[float] = None) -> dict:
        r = self.rings[ring_id]
        if not r.paired:
            return {"ok": False, "reason": "NOT_PAIRED", "fallback": self.fallback_mode}
        if not r.calibrated:
            self.fallback_mode = "host_controls"
            return {"ok": False, "reason": "NOT_CALIBRATED", "fallback": self.fallback_mode}
        ts = now if now is not None else time.time()
        age = ts - r.last_cal_ts
        drift = r.drift_per_s * age
        corrected = [raw[i] - r.offset[i] + drift for i in range(3)]
        mag = math.sqrt(sum(x * x for x in corrected))
        if mag > 2.5:  # drift/fault threshold
            self.fallback_mode = "gesture_disabled"
            return {"ok": False, "reason": "DRIFT_EXCEEDED", "fallback": self.fallback_mode, "mag": mag}
        return {"ok": True, "corrected": corrected, "fallback": "none", "evidence_class": "SIMULATED"}
