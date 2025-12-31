"""Drop-in replacement for Python's hashlib module.

This module provides the same API as Python's hashlib module.
Future versions may use Go's crypto packages for performance when available.

Usage:
    from goated.compat import hashlib

    # Same API as stdlib hashlib
    h = hashlib.sha256(b'hello')
    print(h.hexdigest())
"""

from __future__ import annotations

# Re-export everything from Python's hashlib module
from hashlib import (
    algorithms_available,
    algorithms_guaranteed,
    blake2b,
    blake2s,
    md5,
    new,
    sha1,
    sha3_224,
    sha3_256,
    sha3_384,
    sha3_512,
    sha224,
    sha256,
    sha384,
    sha512,
)

# file_digest was added in Python 3.11
try:
    from hashlib import file_digest  # type: ignore[attr-defined]
except ImportError:
    from collections.abc import Callable
    from typing import Any, BinaryIO

    def file_digest(
        fileobj: BinaryIO,
        digest: str | Callable[[], Any],
        *,
        _bufsize: int = 262144,
    ) -> Any:
        """Hash the contents of a file-like object."""
        h = new(digest) if isinstance(digest, str) else digest()
        buf = fileobj.read(_bufsize)
        while buf:
            h.update(buf)
            buf = fileobj.read(_bufsize)
        return h


__all__ = [
    "new",
    "md5",
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
    "sha3_224",
    "sha3_256",
    "sha3_384",
    "sha3_512",
    "blake2b",
    "blake2s",
    "algorithms_available",
    "algorithms_guaranteed",
    "file_digest",
]
