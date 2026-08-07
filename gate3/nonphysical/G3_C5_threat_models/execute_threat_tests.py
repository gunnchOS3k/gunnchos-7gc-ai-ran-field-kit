"""Map threat model entries to pytest node ids (executable threat model)."""
from __future__ import annotations
from pathlib import Path
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

MODEL = Path(__file__).with_name("threat_model.yaml")

def listed_tests() -> list[str]:
    data = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    return [t["test"] for t in data.get("threats") or []]
