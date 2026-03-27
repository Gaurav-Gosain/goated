"""High-performance batch operations - the real speed advantage.

These functions do many operations in a single FFI call, letting Go's
goroutines parallelize the work. This amortizes the FFI overhead and
delivers 2-10x speedups over Python's stdlib.

Usage:
    from goated.batch import batch_sha256, batch_gzip_compress, batch_b64encode

    # Hash 1000 items in parallel (3-4x faster than sequential Python)
    hashes = batch_sha256([data1, data2, ...])

    # Compress 1000 items in parallel
    compressed = batch_gzip_compress([data1, data2, ...])
"""

from __future__ import annotations

import ctypes
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False


def _setup() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib

        # Batch gzip compress
        lib.goated_batch_gzip_compress.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.goated_batch_gzip_compress.restype = None

        # Batch gzip decompress
        lib.goated_batch_gzip_decompress.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.goated_batch_gzip_decompress.restype = None

        # Batch base64 encode
        lib.goated_batch_base64_encode.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_batch_base64_encode.restype = None

        # Batch base64 decode
        lib.goated_batch_base64_decode.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.goated_batch_base64_decode.restype = None

        # Batch JSON validate
        lib.goated_batch_json_valid.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_bool),
        ]
        lib.goated_batch_json_valid.restype = None

        # Batch regex match
        lib.goated_batch_regexp_match.argtypes = [
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_bool),
        ]
        lib.goated_batch_regexp_match.restype = None

        # Free helpers
        lib.goated_batch_free_buffers.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
        lib.goated_batch_free_buffers.restype = None
        lib.goated_parallel_free_strings.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
        lib.goated_parallel_free_strings.restype = None

        # Regex compile
        lib.goated_regexp_compile.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        lib.goated_regexp_compile.restype = ctypes.c_uint64
        lib.goated_handle_delete.argtypes = [ctypes.c_uint64]
        lib.goated_handle_delete.restype = None

        _lib_setup = True
    except Exception:
        pass


def _ensure_setup() -> Any:
    _setup()
    if not _lib_setup:
        raise RuntimeError("Go library not available")
    return get_lib().lib


def batch_sha256(items: list[bytes]) -> list[str]:
    """Hash N items with SHA256 in parallel using goroutines.

    Returns list of hex digest strings. 3-4x faster than sequential Python.
    """
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultArray = ctypes.c_char_p * n

    data_ptrs = DataArray(*items)
    data_lens = IntArray(*(len(d) for d in items))
    results = ResultArray()

    lib.goated_parallel_hash_sha256_batch(data_ptrs, data_lens, n, results)
    out = [results[i].decode("ascii") for i in range(n)]
    lib.goated_parallel_free_strings(results, n)
    return out


def batch_sha512(items: list[bytes]) -> list[str]:
    """Hash N items with SHA512 in parallel using goroutines."""
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultArray = ctypes.c_char_p * n

    data_ptrs = DataArray(*items)
    data_lens = IntArray(*(len(d) for d in items))
    results = ResultArray()

    lib.goated_parallel_hash_sha512_batch(data_ptrs, data_lens, n, results)
    out = [results[i].decode("ascii") for i in range(n)]
    lib.goated_parallel_free_strings(results, n)
    return out


def batch_md5(items: list[bytes]) -> list[str]:
    """Hash N items with MD5 in parallel using goroutines."""
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultArray = ctypes.c_char_p * n

    data_ptrs = DataArray(*items)
    data_lens = IntArray(*(len(d) for d in items))
    results = ResultArray()

    lib.goated_parallel_hash_md5_batch(data_ptrs, data_lens, n, results)
    out = [results[i].decode("ascii") for i in range(n)]
    lib.goated_parallel_free_strings(results, n)
    return out


def batch_gzip_compress(items: list[bytes], level: int = 6) -> list[bytes]:
    """Gzip compress N items in parallel using goroutines.

    Returns list of compressed bytes. 2-5x faster than sequential Python.
    """
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    PtrArray = ctypes.c_void_p * n

    data_ptrs = DataArray(*items)
    data_lens = IntArray(*(len(d) for d in items))
    results = PtrArray()
    result_lens = IntArray()

    lib.goated_batch_gzip_compress(data_ptrs, data_lens, n, level, results, result_lens)

    out = []
    for i in range(n):
        if results[i] and result_lens[i] > 0:
            out.append(ctypes.string_at(results[i], result_lens[i]))
        else:
            out.append(b"")
    lib.goated_batch_free_buffers(ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)), n)
    return out


def batch_gzip_decompress(items: list[bytes]) -> list[bytes]:
    """Gzip decompress N items in parallel using goroutines."""
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    PtrArray = ctypes.c_void_p * n

    data_ptrs = DataArray(*items)
    data_lens = IntArray(*(len(d) for d in items))
    results = PtrArray()
    result_lens = IntArray()

    lib.goated_batch_gzip_decompress(data_ptrs, data_lens, n, results, result_lens)

    out = []
    for i in range(n):
        if results[i] and result_lens[i] > 0:
            out.append(ctypes.string_at(results[i], result_lens[i]))
        else:
            out.append(b"")
    lib.goated_batch_free_buffers(ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)), n)
    return out


def batch_b64encode(items: list[bytes]) -> list[bytes]:
    """Base64 encode N items in parallel using goroutines."""
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultArray = ctypes.c_char_p * n

    data_ptrs = DataArray(*items)
    data_lens = IntArray(*(len(d) for d in items))
    results = ResultArray()

    lib.goated_batch_base64_encode(data_ptrs, data_lens, n, results)
    out = [results[i] for i in range(n)]
    lib.goated_parallel_free_strings(results, n)
    return out


def batch_b64decode(items: list[bytes | str]) -> list[bytes]:
    """Base64 decode N items in parallel using goroutines."""
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    PtrArray = ctypes.c_void_p * n
    IntArray = ctypes.c_int * n

    encoded = [s.encode("ascii") if isinstance(s, str) else s for s in items]
    data_ptrs = DataArray(*encoded)
    results = PtrArray()
    result_lens = IntArray()

    lib.goated_batch_base64_decode(data_ptrs, n, results, result_lens)
    out = []
    for i in range(n):
        if results[i] and result_lens[i] > 0:
            out.append(ctypes.string_at(results[i], result_lens[i]))
        else:
            out.append(b"")
    lib.goated_batch_free_buffers(ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)), n)
    return out


def batch_json_valid(items: list[str | bytes]) -> list[bool]:
    """Validate N JSON strings in parallel using goroutines."""
    lib = _ensure_setup()
    n = len(items)
    DataArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    BoolArray = ctypes.c_bool * n

    encoded = [s.encode("utf-8") if isinstance(s, str) else s for s in items]
    data_ptrs = DataArray(*encoded)
    data_lens = IntArray(*(len(d) for d in encoded))
    results = BoolArray()

    lib.goated_batch_json_valid(data_ptrs, data_lens, n, results)
    return [bool(results[i]) for i in range(n)]


def batch_regex_match(pattern: str, texts: list[str]) -> list[bool]:
    """Match N strings against a regex pattern in parallel using goroutines.

    Uses Go's RE2 engine. Compiles the pattern once, matches N strings
    in parallel across CPU cores.
    """
    lib = _ensure_setup()
    n = len(texts)

    # Compile pattern
    err_out = ctypes.c_char_p()
    handle = lib.goated_regexp_compile(pattern.encode("utf-8"), ctypes.byref(err_out))
    if not handle or err_out.value:
        raise ValueError(f"Invalid pattern: {err_out.value.decode()}")

    try:
        TextArray = ctypes.c_char_p * n
        BoolArray = ctypes.c_bool * n

        text_ptrs = TextArray(*(t.encode("utf-8") for t in texts))
        results = BoolArray()

        lib.goated_batch_regexp_match(handle, text_ptrs, n, results)
        return [bool(results[i]) for i in range(n)]
    finally:
        lib.goated_handle_delete(handle)


__all__ = [
    "batch_sha256",
    "batch_sha512",
    "batch_md5",
    "batch_gzip_compress",
    "batch_gzip_decompress",
    "batch_b64encode",
    "batch_b64decode",
    "batch_json_valid",
    "batch_regex_match",
]
