"""Drop-in replacement for Python's zlib module, backed by Go's compress/zlib.

Uses Go FFI for compress/decompress and CRC32/Adler32 checksums.
Falls back to Python for streaming (compressobj/decompressobj).

Usage:
    from goated.compat import zlib
    compressed = zlib.compress(b"data")
    original = zlib.decompress(compressed)
    checksum = zlib.crc32(b"data")
"""

from __future__ import annotations

import ctypes
import zlib as _zlib

# Re-export streaming and constants unchanged
from zlib import (  # noqa: F401
    DEF_BUF_SIZE,
    DEF_MEM_LEVEL,
    DEFLATED,
    MAX_WBITS,
    Z_BEST_COMPRESSION,
    Z_BEST_SPEED,
    Z_DEFAULT_COMPRESSION,
    Z_DEFAULT_STRATEGY,
    Z_FILTERED,
    Z_FINISH,
    Z_HUFFMAN_ONLY,
    Z_NO_COMPRESSION,
    Z_SYNC_FLUSH,
    compressobj,
    decompressobj,
    error,
)

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 16384  # Go zlib only wins above 16KB (Python's C zlib is very fast)
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_zlib_compress.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
        ]
        lib.goated_zlib_compress.restype = ctypes.c_void_p
        lib.goated_zlib_decompress.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_zlib_decompress.restype = ctypes.c_void_p
        lib.goated_crc32_checksum.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.goated_crc32_checksum.restype = ctypes.c_uint
        lib.goated_adler32_checksum.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.goated_adler32_checksum.restype = ctypes.c_uint
        lib.goated_free_bytes.argtypes = [ctypes.c_char_p]
        lib.goated_free_bytes.restype = None
        _lib_setup = True
    except Exception:
        pass


def compress(data: bytes, level: int = Z_DEFAULT_COMPRESSION, wbits: int = MAX_WBITS) -> bytes:
    """Compress data. Go-accelerated for large inputs with default wbits."""
    if wbits != MAX_WBITS or len(data) < _GO_THRESHOLD:
        return _zlib.compress(data, level)
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                out_len = ctypes.c_int()
                ptr = lib.goated_zlib_compress(data, len(data), level, ctypes.byref(out_len))
                if ptr and out_len.value > 0:
                    result = ctypes.string_at(ptr, out_len.value)
                    lib.goated_free_bytes(ctypes.cast(ptr, ctypes.c_char_p))
                    return result
            except Exception:
                pass
    return _zlib.compress(data, level)


def decompress(data: bytes, wbits: int = MAX_WBITS, bufsize: int = DEF_BUF_SIZE) -> bytes:
    """Decompress data. Go-accelerated for large inputs with default wbits."""
    if wbits != MAX_WBITS or len(data) < _GO_THRESHOLD:
        return _zlib.decompress(data, wbits, bufsize)
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                out_len = ctypes.c_int()
                err_out = ctypes.c_char_p()
                ptr = lib.goated_zlib_decompress(
                    data, len(data), ctypes.byref(out_len), ctypes.byref(err_out),
                )
                if ptr and not err_out.value and out_len.value > 0:
                    result = ctypes.string_at(ptr, out_len.value)
                    lib.goated_free_bytes(ctypes.cast(ptr, ctypes.c_char_p))
                    return result
            except Exception:
                pass
    return _zlib.decompress(data, wbits, bufsize)


def crc32(data: bytes, value: int = 0) -> int:
    """Compute CRC32 checksum. Uses Python's C-optimized zlib.crc32 (fastest)."""
    # Python's zlib.crc32 is a direct C call to zlib - unbeatable by FFI
    return _zlib.crc32(data, value)


def adler32(data: bytes, value: int = 1) -> int:
    """Compute Adler32 checksum. Uses Python's C-optimized zlib.adler32 (fastest)."""
    # Python's zlib.adler32 is a direct C call - unbeatable by FFI
    return _zlib.adler32(data, value)


__all__ = [
    "compress",
    "decompress",
    "compressobj",
    "decompressobj",
    "crc32",
    "adler32",
    "error",
    "DEFLATED",
    "DEF_BUF_SIZE",
    "DEF_MEM_LEVEL",
    "MAX_WBITS",
    "Z_BEST_COMPRESSION",
    "Z_BEST_SPEED",
    "Z_DEFAULT_COMPRESSION",
    "Z_DEFAULT_STRATEGY",
    "Z_FILTERED",
    "Z_FINISH",
    "Z_HUFFMAN_ONLY",
    "Z_NO_COMPRESSION",
    "Z_SYNC_FLUSH",
]
