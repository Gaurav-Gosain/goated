"""Drop-in replacement for Python's base64 module.

This module provides the same API as Python's base64 module.
Future versions may use Go's encoding/base64 for performance when available.

Usage:
    from goated.compat import base64

    # Same API as stdlib base64
    encoded = base64.b64encode(b'hello')
    decoded = base64.b64decode(encoded)
"""

from __future__ import annotations

# Re-export everything from Python's base64 module
from base64 import (
    a85decode,
    # ASCII85 / Base85
    a85encode,
    b16decode,
    # Base16 (hex)
    b16encode,
    b32decode,
    # Base32
    b32encode,
    b64decode,
    # Standard Base64
    b64encode,
    b85decode,
    b85encode,
    decode,
    decodebytes,
    # Legacy
    encode,
    encodebytes,
    standard_b64decode,
    standard_b64encode,
    urlsafe_b64decode,
    # URL-safe Base64
    urlsafe_b64encode,
)

# b32hexencode/b32hexdecode were added in Python 3.10
try:
    from base64 import b32hexdecode, b32hexencode
except ImportError:
    from typing import Any

    def b32hexencode(s: Any) -> bytes:  # type: ignore[misc]
        """Encode bytes using Base32hex."""
        return b32encode(s)

    def b32hexdecode(s: Any, casefold: bool = False) -> bytes:  # type: ignore[misc]
        """Decode Base32hex encoded bytes."""
        return b32decode(s, casefold)


__all__ = [
    # Standard Base64
    "b64encode",
    "b64decode",
    "standard_b64encode",
    "standard_b64decode",
    # URL-safe Base64
    "urlsafe_b64encode",
    "urlsafe_b64decode",
    # Base32
    "b32encode",
    "b32decode",
    "b32hexencode",
    "b32hexdecode",
    # Base16 (hex)
    "b16encode",
    "b16decode",
    # ASCII85 / Base85
    "a85encode",
    "a85decode",
    "b85encode",
    "b85decode",
    # Legacy
    "encode",
    "decode",
    "encodebytes",
    "decodebytes",
]
