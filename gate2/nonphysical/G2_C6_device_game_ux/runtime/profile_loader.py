"""Load device×game UX runtime profiles."""
from __future__ import annotations
from pathlib import Path
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

MATRIX = Path(__file__).resolve().parents[1] / "profiles" / "device_game_ux_matrix.yaml"

def load_matrix() -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml required")
    return yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

def resolve(game_id: str, device_id: str) -> dict:
    m = load_matrix()
    game = (m.get("games") or {})[game_id]
    role = (game.get("device_roles") or {})[device_id]
    return {"game_id": game_id, "device_id": device_id, "vision": game["vision"], "role": role}
