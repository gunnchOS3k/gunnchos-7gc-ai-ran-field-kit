"""Cross-device identity + continuity tokens (NONPHYSICAL)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import hashlib, time, uuid

@dataclass
class DeviceIdentity:
    device_id: str
    public_key_fingerprint: str
    roles: List[str]

@dataclass
class ContinuityStore:
    account_id: str
    devices: Dict[str, DeviceIdentity] = field(default_factory=dict)
    session_epoch: int = 0

    def enroll(self, device_id: str, pubkey: bytes, roles: List[str]) -> DeviceIdentity:
        fp = hashlib.sha256(pubkey).hexdigest()[:16]
        ident = DeviceIdentity(device_id, fp, roles)
        self.devices[device_id] = ident
        self.session_epoch += 1
        return ident

    def continuity_token(self, device_id: str) -> str:
        d = self.devices[device_id]
        raw = f"{self.account_id}:{d.device_id}:{d.public_key_fingerprint}:{self.session_epoch}".encode()
        return hashlib.sha256(raw).hexdigest()

    def transfer_session(self, from_id: str, to_id: str) -> dict:
        if from_id not in self.devices or to_id not in self.devices:
            return {"ok": False, "reason": "UNKNOWN_DEVICE"}
        self.session_epoch += 1
        return {
            "ok": True,
            "from": from_id,
            "to": to_id,
            "token": self.continuity_token(to_id),
            "evidence_class": "SOFTWARE",
        }
