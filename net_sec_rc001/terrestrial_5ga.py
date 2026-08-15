"""Deprecated alias — Rel-16 surface lives in terrestrial_rel16.py.

Kept so old imports fail loudly toward the honest module name.
"""
from .terrestrial_rel16 import CLAIM, RM520NTerrestrialDigital

__all__ = ["CLAIM", "RM520NTerrestrialDigital"]
