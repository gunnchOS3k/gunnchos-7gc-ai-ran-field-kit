"""Gate 0 ecosystem control plane for gunnchOS3k."""

__version__ = "0.1.0"
INGESTION_SCRIPT_VERSION = "1.0.0"

# Status tokens — never emit GATE_0_PASS without Edmund approval evidence.
STATUS_AUTOMATED_PASS = "GATE_0_AUTOMATED_PASS"
STATUS_AUTOMATED_PARTIAL = "GATE_0_AUTOMATED_PARTIAL"
STATUS_CHARTER_PENDING = "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND"
STATUS_GATE_0_PASS = "GATE_0_PASS"  # prohibited without approval record
