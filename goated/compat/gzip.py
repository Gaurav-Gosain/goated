"""Drop-in replacement for Python's gzip module, backed by Go's compress/gzip.

Uses Go FFI for compress/decompress of complete buffers.
Falls back to Python for streaming (GzipFile, open).

Usage:
    from goated.compat import gzip
    compressed = gzip.compress(b"data")
    original = gzip.decompress(compressed)
"""

from __future__ import annotations

import ctypes
import gzip as _gzip

# Re-export streaming/file APIs unchanged
from gzip import (  # noqa: F401
    BadGzipFile,
    GzipFile,
    open,
)

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 8192  # Go gzip.NewWriter has ~100μs setup; only worth it above 8KB
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        # Use c_void_p for return type to avoid null-byte truncation
        lib.goated_gzip_compress.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
        ]
        lib.goated_gzip_compress.restype = ctypes.c_void_p
        lib.goated_gzip_decompress.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_gzip_decompress.restype = ctypes.c_void_p
        lib.goated_free_bytes.argtypes = [ctypes.c_char_p]
        lib.goated_free_bytes.restype = None
        _lib_setup = True
    except Exception:
        pass


def compress(data: bytes, compresslevel: int = 9, mtime: float | None = None) -> bytes:
    """Compress data using gzip. Go-accelerated for large inputs."""
    if mtime is not None or len(data) < _GO_THRESHOLD:
        return _gzip.compress(data, compresslevel=compresslevel, mtime=mtime)
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                out_len = ctypes.c_int()
                ptr = lib.goated_gzip_compress(data, len(data), compresslevel, ctypes.byref(out_len))
                if ptr and out_len.value > 0:
                    result = ctypes.string_at(ptr, out_len.value)
                    lib.goated_free_bytes(ctypes.cast(ptr, ctypes.c_char_p))
                    return result
            except Exception:
                pass
    return _gzip.compress(data, compresslevel=compresslevel)


def decompress(data: bytes) -> bytes:
    """Decompress gzip data. Go-accelerated for large inputs."""
    if len(data) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _gzip.decompress(data)
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            out_len = ctypes.c_int()
            err_out = ctypes.c_char_p()
            ptr = lib.goated_gzip_decompress(
                data, len(data), ctypes.byref(out_len), ctypes.byref(err_out),
            )
            if ptr and not err_out.value and out_len.value > 0:
                result = ctypes.string_at(ptr, out_len.value)
                lib.goated_free_bytes(ctypes.cast(ptr, ctypes.c_char_p))
                return result
        except Exception:
            pass
    return _gzip.decompress(data)


__all__ = [
    "compress",
    "decompress",
    "open",
    "GzipFile",
    "BadGzipFile",
]
