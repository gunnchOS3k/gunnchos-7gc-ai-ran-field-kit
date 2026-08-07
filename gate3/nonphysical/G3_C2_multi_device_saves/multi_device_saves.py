"""Multi-device save slots with conflict merge (NONPHYSICAL)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class SaveSlot:
    game_id: str
    rev: int
    payload: Dict[str, Any]
    device_id: str

@dataclass
class SaveStore:
    slots: Dict[str, SaveSlot] = field(default_factory=dict)

    def key(self, account: str, game_id: str) -> str:
        return f"{account}:{game_id}"

    def put(self, account: str, game_id: str, device_id: str, payload: Dict[str, Any], rev: Optional[int] = None) -> SaveSlot:
        k = self.key(account, game_id)
        cur = self.slots.get(k)
        new_rev = (cur.rev + 1) if cur else 1
        if rev is not None and cur and rev < cur.rev:
            raise ValueError("CONFLICT_STALE_REV")
        slot = SaveSlot(game_id, new_rev, payload, device_id)
        self.slots[k] = slot
        return slot

    def get(self, account: str, game_id: str) -> Optional[SaveSlot]:
        return self.slots.get(self.key(account, game_id))
