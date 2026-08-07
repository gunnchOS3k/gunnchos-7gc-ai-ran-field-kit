"""5G-LENA / ns-3 external runner alias (GPL-2.0 boundary)."""
from __future__ import annotations

from .lena_ns3 import LenaNs3Adapter


class FivegLenaExternalAdapter(LenaNs3Adapter):
    tool_id = "fiveg_lena_ns3"
