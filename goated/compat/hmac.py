"""Drop-in replacement for Python's hmac module, backed by Go's crypto/hmac.

Uses Go FFI for one-shot HMAC computation (digest function).
Falls back to Python for streaming HMAC objects.

Usage:
    from goated.compat import hmac
    sig = hmac.digest(key, msg, "sha256")
"""

from __future__ import annotations

import ctypes
import hmac as _hmac

# Re-export everything from Python's hmac
from hmac import (  # noqa: F401
    compare_digest,
    new,
)
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False
_GO_FUNCS: dict[str, Any] = {}


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        for name in ("sha1", "sha256", "sha512"):
            fn = getattr(lib, f"goated_hmac_{name}")
            fn.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
            fn.restype = ctypes.c_char_p
            _GO_FUNCS[name] = fn
        _lib_setup = True
    except Exception:
        pass


def digest(key: bytes, msg: bytes, digest: str | Any) -> bytes:
    """One-shot HMAC digest. Go-accelerated for sha1/sha256/sha512."""
    algo_name = digest if isinstance(digest, str) else getattr(digest, "name", digest.__name__)
    if _USE_GO_LIB and algo_name in ("sha1", "sha256", "sha512"):
        _setup_lib()
        fn = _GO_FUNCS.get(algo_name)
        if fn is not None:
            try:
                result = fn(key, len(key), msg, len(msg))
                if result:
                    hex_str = result.decode("ascii")
                    return bytes.fromhex(hex_str)
            except Exception:
                pass
    return _hmac.digest(key, msg, digest)


__all__ = [
    "new",
    "compare_digest",
    "digest",
]
