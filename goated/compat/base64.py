"""Drop-in replacement for Python's base64 module, backed by Go's encoding/base64.

Uses Go FFI for large payloads (>1KB), falls back to Python for small data.

Usage:
    from goated.compat import base64
    encoded = base64.b64encode(b"data")
    decoded = base64.b64decode(encoded)
"""

from __future__ import annotations

import ctypes

# Re-export everything from Python's base64
from base64 import (  # noqa: F401
    a85decode,
    a85encode,
    b16decode,
    b16encode,
    b32decode,
    b32encode,
    b85decode,
    b85encode,
    decode,
    decodebytes,
    encode,
    encodebytes,
    standard_b64decode,
    standard_b64encode,
)
from base64 import (
    b64decode as _py_b64decode,
)
from base64 import (
    b64encode as _py_b64encode,
)
from base64 import (
    urlsafe_b64decode as _py_urlsafe_b64decode,
)
from base64 import (
    urlsafe_b64encode as _py_urlsafe_b64encode,
)
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 262144  # Python binascii is C-optimized; Go only wins for decode >256KB
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_base64_std_encode.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.goated_base64_std_encode.restype = ctypes.c_char_p
        lib.goated_base64_std_decode.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_base64_std_decode.restype = ctypes.c_void_p
        lib.goated_base64_url_encode.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.goated_base64_url_encode.restype = ctypes.c_char_p
        lib.goated_base64_url_decode.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_base64_url_decode.restype = ctypes.c_void_p
        _lib_setup = True
    except Exception:
        pass


def b64encode(s: bytes, altchars: bytes | None = None) -> bytes:
    """Encode bytes using Base64. Go-accelerated for large inputs."""
    if altchars is not None or len(s) < _GO_THRESHOLD:
        return _py_b64encode(s)
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                result = lib.goated_base64_std_encode(s, len(s))
                if result:
                    return result
            except Exception:
                pass
    return _py_b64encode(s)


def b64decode(s: bytes | str, altchars: bytes | None = None, validate: bool = False) -> bytes:
    """Decode Base64 encoded bytes. Go-accelerated for large inputs."""
    if altchars is not None or validate:
        return _py_b64decode(s, altchars, validate)
    if isinstance(s, str):
        s = s.encode("ascii")
    if len(s) < _GO_THRESHOLD:
        return _py_b64decode(s)
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                out_len = ctypes.c_int()
                err_out = ctypes.c_char_p()
                ptr = lib.goated_base64_std_decode(s, ctypes.byref(out_len), ctypes.byref(err_out))
                if ptr and not err_out.value:
                    return ctypes.string_at(ptr, out_len.value)
            except Exception:
                pass
    return _py_b64decode(s)


def urlsafe_b64encode(s: bytes) -> bytes:
    """Encode bytes using URL-safe Base64. Go-accelerated for large inputs."""
    if len(s) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _py_urlsafe_b64encode(s)
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            result = lib.goated_base64_url_encode(s, len(s))
            if result:
                return result
        except Exception:
            pass
    return _py_urlsafe_b64encode(s)


def urlsafe_b64decode(s: bytes | str) -> bytes:
    """Decode URL-safe Base64 encoded bytes. Go-accelerated for large inputs."""
    if isinstance(s, str):
        s = s.encode("ascii")
    if len(s) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _py_urlsafe_b64decode(s)
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            out_len = ctypes.c_int()
            err_out = ctypes.c_char_p()
            ptr = lib.goated_base64_url_decode(s, ctypes.byref(out_len), ctypes.byref(err_out))
            if ptr and not err_out.value:
                return ctypes.string_at(ptr, out_len.value)
        except Exception:
            pass
    return _py_urlsafe_b64decode(s)


try:
    from base64 import b32hexdecode, b32hexencode  # noqa: F401
except ImportError:

    def b32hexencode(s: Any) -> bytes:
        return b32encode(s)

    def b32hexdecode(s: Any, casefold: bool = False) -> bytes:
        return b32decode(s, casefold)


__all__ = [
    "b64encode",
    "b64decode",
    "b32encode",
    "b32decode",
    "b16encode",
    "b16decode",
    "a85encode",
    "a85decode",
    "b85encode",
    "b85decode",
    "urlsafe_b64encode",
    "urlsafe_b64decode",
    "standard_b64encode",
    "standard_b64decode",
    "encode",
    "encodebytes",
    "decode",
    "decodebytes",
]
