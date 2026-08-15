"""NET-SEC-6G-RC-001 digital control-plane package.

Product wording:
5G-Advanced and NTN-capable, IMT-2030-aligned, software-defined, and engineered
for migration to standardized 6G.

Never claims final standardized 6G / carrier acceptance / real NTN modem validation.
"""
from .evaluate import evaluate_net_sec_rc001
from .tokens import TOKEN_TABLE, FORBIDDEN_TOKENS

__all__ = ["evaluate_net_sec_rc001", "TOKEN_TABLE", "FORBIDDEN_TOKENS"]
