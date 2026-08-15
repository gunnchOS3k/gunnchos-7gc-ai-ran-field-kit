"""Semantic Continuity for Equitable NTN Education — digital executed traces via R6G-008.

Kept as a thin compatibility entrypoint; execution lives in r6g008_semantic_ntn.
"""
from __future__ import annotations

from typing import Any

from research.r6g.claim_firewall import assert_no_soa


def run_semantic_continuity() -> dict[str, Any]:
    # Import lazily to avoid circular import at module load.
    from research.r6g.experiments.r6g008_semantic_ntn import run_r6g008

    full = run_r6g008()
    report = dict(full["semantic_continuity"])
    report["parent_packet"] = "R6G-008"
    report["execution_class"] = full.get("execution_class")
    report["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] = True
    assert_no_soa(report)
    return report
