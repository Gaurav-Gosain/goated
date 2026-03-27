"""Drop-in replacement for Python's struct module.

Python's struct format strings are very Python-specific and the C-accelerated
implementation is already fast. This module is provided for completeness of
the compat namespace and passes all operations through to Python's struct.

Usage:
    from goated.compat import struct
    packed = struct.pack(">I", 42)
    (value,) = struct.unpack(">I", packed)
"""

from __future__ import annotations

# Re-export everything from Python's struct module
from struct import (  # noqa: F401
    Struct,
    calcsize,
    error,
    iter_unpack,
    pack,
    pack_into,
    unpack,
    unpack_from,
)

__all__ = [
    "pack",
    "pack_into",
    "unpack",
    "unpack_from",
    "iter_unpack",
    "calcsize",
    "error",
    "Struct",
]
