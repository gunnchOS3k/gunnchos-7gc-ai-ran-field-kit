"""Secure boot chain emulator (NONPHYSICAL)."""
from __future__ import annotations
import hashlib, hmac
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class SignedImage:
    name: str
    payload: bytes
    key_id: str
    signature: bytes
    version: int

@dataclass
class SecureBootEmulator:
    trust_store: Dict[str, bytes]  # key_id -> secret (HMAC-SHA256 stand-in)
    anti_rollback: Dict[str, int] = field(default_factory=dict)

    def sign(self, name: str, payload: bytes, key_id: str, version: int) -> SignedImage:
        key = self.trust_store[key_id]
        sig = hmac.new(key, payload + name.encode() + str(version).encode(), hashlib.sha256).digest()
        return SignedImage(name, payload, key_id, sig, version)

    def verify(self, image: SignedImage) -> bool:
        key = self.trust_store.get(image.key_id)
        if key is None:
            return False
        expected = hmac.new(key, image.payload + image.name.encode() + str(image.version).encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, image.signature):
            return False
        prev = self.anti_rollback.get(image.name, 0)
        if image.version < prev:
            return False
        self.anti_rollback[image.name] = max(prev, image.version)
        return True
