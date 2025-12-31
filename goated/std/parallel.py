"""Parallel processing using Go goroutines.

This module exposes Go's goroutine-based parallelism to Python,
allowing efficient batch operations that bypass Python's GIL.
"""

from __future__ import annotations

import ctypes
from collections.abc import Sequence
from typing import TypeVar

from goated._core import _USE_GO_LIB, get_lib

__all__ = [
    "num_cpus",
    "parallel_hash_md5",
    "parallel_hash_sha1",
    "parallel_hash_sha256",
    "parallel_hash_sha512",
    "parallel_map_upper",
    "parallel_map_lower",
    "parallel_contains",
]

T = TypeVar("T")

_lib = get_lib() if _USE_GO_LIB else None


def num_cpus() -> int:
    """Returns the number of CPUs available for parallel processing."""
    if _lib:
        try:
            _lib.goated_parallel_num_cpu.restype = ctypes.c_int
            return int(_lib.goated_parallel_num_cpu())
        except Exception:
            pass
    import os

    return os.cpu_count() or 1


def parallel_hash_md5(data_list: Sequence[bytes]) -> list[str]:
    """Hash multiple byte sequences with MD5 in parallel using Go goroutines."""
    if not _lib or len(data_list) < 2:
        import hashlib

        return [hashlib.md5(d).hexdigest() for d in data_list]

    n = len(data_list)

    # Create arrays for data pointers and lengths
    DataPtrArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultPtrArray = ctypes.c_char_p * n

    data_ptrs = DataPtrArray()
    data_lens = IntArray()
    results = ResultPtrArray()

    for i, d in enumerate(data_list):
        data_ptrs[i] = d
        data_lens[i] = len(d)

    try:
        _lib.goated_parallel_hash_md5_batch(
            ctypes.cast(data_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.cast(data_lens, ctypes.POINTER(ctypes.c_int)),
            ctypes.c_int(n),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
        )

        result_list = [r.decode("utf-8") if (r := results[i]) is not None else "" for i in range(n)]

        # Free the allocated strings
        _lib.goated_parallel_free_strings(
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
        )

        return result_list
    except Exception:
        import hashlib

        return [hashlib.md5(d).hexdigest() for d in data_list]


def parallel_hash_sha256(data_list: Sequence[bytes]) -> list[str]:
    """Hash multiple byte sequences with SHA256 in parallel using Go goroutines."""
    if not _lib or len(data_list) < 2:
        import hashlib

        return [hashlib.sha256(d).hexdigest() for d in data_list]

    n = len(data_list)

    DataPtrArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultPtrArray = ctypes.c_char_p * n

    data_ptrs = DataPtrArray()
    data_lens = IntArray()
    results = ResultPtrArray()

    for i, d in enumerate(data_list):
        data_ptrs[i] = d
        data_lens[i] = len(d)

    try:
        _lib.goated_parallel_hash_sha256_batch(
            ctypes.cast(data_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.cast(data_lens, ctypes.POINTER(ctypes.c_int)),
            ctypes.c_int(n),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
        )

        result_list = [r.decode("utf-8") if (r := results[i]) is not None else "" for i in range(n)]

        _lib.goated_parallel_free_strings(
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
        )

        return result_list
    except Exception:
        import hashlib

        return [hashlib.sha256(d).hexdigest() for d in data_list]


def parallel_hash_sha512(data_list: Sequence[bytes]) -> list[str]:
    """Hash multiple byte sequences with SHA512 in parallel using Go goroutines."""
    if not _lib or len(data_list) < 2:
        import hashlib

        return [hashlib.sha512(d).hexdigest() for d in data_list]

    n = len(data_list)

    DataPtrArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultPtrArray = ctypes.c_char_p * n

    data_ptrs = DataPtrArray()
    data_lens = IntArray()
    results = ResultPtrArray()

    for i, d in enumerate(data_list):
        data_ptrs[i] = d
        data_lens[i] = len(d)

    try:
        _lib.goated_parallel_hash_sha512_batch(
            ctypes.cast(data_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.cast(data_lens, ctypes.POINTER(ctypes.c_int)),
            ctypes.c_int(n),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
        )

        result_list = [r.decode("utf-8") if (r := results[i]) is not None else "" for i in range(n)]

        _lib.goated_parallel_free_strings(
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
        )

        return result_list
    except Exception:
        import hashlib

        return [hashlib.sha512(d).hexdigest() for d in data_list]


def parallel_hash_sha1(data_list: Sequence[bytes]) -> list[str]:
    """Hash multiple byte sequences with SHA1 in parallel using Go goroutines."""
    if not _lib or len(data_list) < 2:
        import hashlib

        return [hashlib.sha1(d).hexdigest() for d in data_list]

    n = len(data_list)

    DataPtrArray = ctypes.c_char_p * n
    IntArray = ctypes.c_int * n
    ResultPtrArray = ctypes.c_char_p * n

    data_ptrs = DataPtrArray()
    data_lens = IntArray()
    results = ResultPtrArray()

    for i, d in enumerate(data_list):
        data_ptrs[i] = d
        data_lens[i] = len(d)

    try:
        _lib.goated_parallel_hash_sha1_batch(
            ctypes.cast(data_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.cast(data_lens, ctypes.POINTER(ctypes.c_int)),
            ctypes.c_int(n),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
        )

        result_list = [r.decode("utf-8") if (r := results[i]) is not None else "" for i in range(n)]

        _lib.goated_parallel_free_strings(
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
        )

        return result_list
    except Exception:
        import hashlib

        return [hashlib.sha1(d).hexdigest() for d in data_list]


def parallel_map_upper(strings: Sequence[str]) -> list[str]:
    """Convert multiple strings to uppercase in parallel using Go goroutines.

    Args:
        strings: List of strings to convert

    Returns:
        List of uppercase strings

    """
    if not _lib or len(strings) < 10:
        return [s.upper() for s in strings]

    n = len(strings)

    StrPtrArray = ctypes.c_char_p * n
    ResultPtrArray = ctypes.c_char_p * n

    str_ptrs = StrPtrArray()
    results = ResultPtrArray()

    for i, s in enumerate(strings):
        str_ptrs[i] = s.encode("utf-8")

    try:
        _lib.goated_parallel_map_toupper(
            ctypes.cast(str_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
        )

        result_list = [r.decode("utf-8") if (r := results[i]) is not None else "" for i in range(n)]

        _lib.goated_parallel_free_strings(
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
        )

        return result_list
    except Exception:
        return [s.upper() for s in strings]


def parallel_map_lower(strings: Sequence[str]) -> list[str]:
    """Convert multiple strings to lowercase in parallel using Go goroutines.

    Args:
        strings: List of strings to convert

    Returns:
        List of lowercase strings

    """
    if not _lib or len(strings) < 10:
        return [s.lower() for s in strings]

    n = len(strings)

    StrPtrArray = ctypes.c_char_p * n
    ResultPtrArray = ctypes.c_char_p * n

    str_ptrs = StrPtrArray()
    results = ResultPtrArray()

    for i, s in enumerate(strings):
        str_ptrs[i] = s.encode("utf-8")

    try:
        _lib.goated_parallel_map_tolower(
            ctypes.cast(str_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
        )

        result_list = [r.decode("utf-8") if (r := results[i]) is not None else "" for i in range(n)]

        _lib.goated_parallel_free_strings(
            ctypes.cast(results, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
        )

        return result_list
    except Exception:
        return [s.lower() for s in strings]


def parallel_contains(texts: Sequence[str], substr: str) -> list[bool]:
    """Check if multiple strings contain a substring in parallel using Go goroutines.

    Args:
        texts: List of strings to search in
        substr: Substring to search for

    Returns:
        List of booleans indicating whether each text contains the substring

    """
    if not _lib or len(texts) < 10:
        return [substr in t for t in texts]

    n = len(texts)

    StrPtrArray = ctypes.c_char_p * n
    BoolArray = ctypes.c_bool * n

    str_ptrs = StrPtrArray()
    results = BoolArray()

    for i, s in enumerate(texts):
        str_ptrs[i] = s.encode("utf-8")

    try:
        _lib.goated_parallel_strings_contains_batch(
            ctypes.cast(str_ptrs, ctypes.POINTER(ctypes.c_char_p)),
            ctypes.c_int(n),
            substr.encode("utf-8"),
            ctypes.cast(results, ctypes.POINTER(ctypes.c_bool)),
        )

        return [bool(results[i]) for i in range(n)]
    except Exception:
        return [substr in t for t in texts]
