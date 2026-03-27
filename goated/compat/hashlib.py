"""Drop-in replacement for Python's hashlib module, backed by Go's crypto packages.

Provides Go-accelerated one-shot hashing for md5, sha1, sha256, sha512.
Falls back to Python's hashlib for streaming updates and unsupported algorithms.

Usage:
    from goated.compat import hashlib
    digest = hashlib.sha256(b"data").hexdigest()
    # Or use fast one-shot:
    hex_str = hashlib.go_hexdigest("sha256", b"data")
"""

from __future__ import annotations

import ctypes
import hashlib as _hashlib
from collections.abc import Callable

# Re-export everything from Python's hashlib
from hashlib import (  # noqa: F401
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
from typing import Any, BinaryIO

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False
_GO_FUNCS: dict[str, Any] = {}


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        for name in ("md5", "sha1", "sha256", "sha512"):
            fn = getattr(lib, f"goated_crypto_{name}_SumHex")
            fn.argtypes = [ctypes.c_char_p, ctypes.c_int64]
            fn.restype = ctypes.c_char_p
            _GO_FUNCS[name] = fn
        for name in ("sha1", "sha256", "sha512"):
            fn = getattr(lib, f"goated_hmac_{name}")
            fn.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
            fn.restype = ctypes.c_char_p
            _GO_FUNCS[f"hmac_{name}"] = fn
        _lib_setup = True
    except Exception:
        pass


def go_hexdigest(algorithm: str, data: bytes) -> str:
    """One-shot Go-accelerated hex digest. Faster than streaming for complete data."""
    _setup_lib()
    fn = _GO_FUNCS.get(algorithm)
    if fn is not None:
        result = fn(data, len(data))
        if result:
            return result.decode("ascii")
    return _hashlib.new(algorithm, data).hexdigest()


def go_hmac_hexdigest(algorithm: str, key: bytes, msg: bytes) -> str:
    """One-shot Go-accelerated HMAC hex digest."""
    _setup_lib()
    fn = _GO_FUNCS.get(f"hmac_{algorithm}")
    if fn is not None:
        result = fn(key, len(key), msg, len(msg))
        if result:
            return result.decode("ascii")
    import hmac as _hmac

    return _hmac.new(key, msg, algorithm).hexdigest()


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
    "new",
    "file_digest",
    "algorithms_available",
    "algorithms_guaranteed",
    "go_hexdigest",
    "go_hmac_hexdigest",
]
