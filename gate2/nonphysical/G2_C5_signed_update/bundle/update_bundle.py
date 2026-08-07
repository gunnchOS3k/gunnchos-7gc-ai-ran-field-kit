"""Signed update bundle format + install/rollback (NONPHYSICAL)."""
from __future__ import annotations
import hashlib, hmac, json
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class UpdateBundle:
    version: int
    target: str
    payload: bytes
    rollback_min: int
    key_id: str
    signature: bytes = b""

    def manifest_bytes(self) -> bytes:
        m = {
            "version": self.version,
            "target": self.target,
            "rollback_min": self.rollback_min,
            "payload_sha256": hashlib.sha256(self.payload).hexdigest(),
            "key_id": self.key_id,
        }
        return json.dumps(m, sort_keys=True, separators=(",", ":")).encode()

@dataclass
class UpdateAdapter:
    name: str
    keys: Dict[str, bytes]
    installed_version: int = 0
    slot_a: Optional[bytes] = None
    slot_b: Optional[bytes] = None
    active: str = "a"

    def sign(self, bundle: UpdateBundle) -> UpdateBundle:
        key = self.keys[bundle.key_id]
        bundle.signature = hmac.new(key, bundle.manifest_bytes() + bundle.payload, hashlib.sha256).digest()
        return bundle

    def verify(self, bundle: UpdateBundle) -> bool:
        key = self.keys.get(bundle.key_id)
        if not key:
            return False
        expected = hmac.new(key, bundle.manifest_bytes() + bundle.payload, hashlib.sha256).digest()
        return hmac.compare_digest(expected, bundle.signature)

    def install(self, bundle: UpdateBundle) -> str:
        if not self.verify(bundle):
            return "REJECT_SIGNATURE"
        if bundle.version < bundle.rollback_min:
            return "REJECT_POLICY"
        if bundle.version < self.installed_version:
            return "REJECT_DOWNGRADE"
        # A/B flip
        if self.active == "a":
            self.slot_b = bundle.payload
            self.active = "b"
        else:
            self.slot_a = bundle.payload
            self.active = "a"
        prev = self.installed_version
        self.installed_version = bundle.version
        return f"OK_INSTALLED_from_{prev}_to_{bundle.version}"

    def rollback(self) -> str:
        self.active = "a" if self.active == "b" else "b"
        return f"OK_ROLLBACK_active_{self.active}"
