"""NET-SEC-6G-RC-001 digital control-plane package.

Product wording (architecture / migration intent — not RM520N hardware capability):
Software-defined architecture engineered for 5G-Advanced and NTN-capable paths
(NTN via simulation), IMT-2030-aligned, and engineered for migration to
standardized 6G; Quectel RM520N-GL digital baseline is Rel-16 NSA+SA Sub-6
terrestrial only — not 5G-Advanced hardware and not NTN.

Never claims final standardized 6G / carrier acceptance / real NTN modem validation.
5GA_TERRESTRIAL_DIGITAL_RUNTIME remains false until a Rel-18+/5GA digital surface
distinct from the Rel-16 modem path exists.
"""
from .evaluate import evaluate_net_sec_rc001
from .tokens import FORBIDDEN_TOKENS, SUPPORTING_TOKENS, TOKEN_TABLE

__all__ = ["evaluate_net_sec_rc001", "TOKEN_TABLE", "FORBIDDEN_TOKENS", "SUPPORTING_TOKENS"]
