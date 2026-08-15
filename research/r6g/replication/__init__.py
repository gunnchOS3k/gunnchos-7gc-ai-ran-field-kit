"""R6G replication & adoption control plane (no SoA inflation)."""
from research.r6g.replication import reproduce as _reproduce_mod
from research.r6g.replication import verify_independent as _verify_mod

__all__ = ["run_replication_suite", "verify_from_raw"]

run_replication_suite = _reproduce_mod.run_replication_suite
verify_from_raw = _verify_mod.verify_from_raw
