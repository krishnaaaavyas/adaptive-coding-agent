"""Versioned, no-inference Study-1 information protocol.

Legacy experiment execution is deliberately separate. Official admission
requires externally authenticated acquisition, evidence and runtime profiles.
"""

from .core import POLICY_ID, PolicyFailure, canonical_json, digest

__all__ = ["POLICY_ID", "PolicyFailure", "canonical_json", "digest"]
