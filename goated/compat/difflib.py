"""Drop-in replacement for Python's difflib module, backed by Go's diff package.

Uses Go FFI for unified diff generation on large inputs.
Falls back to Python for SequenceMatcher, get_close_matches, etc.

Usage:
    from goated.compat import difflib
    diff = difflib.unified_diff(a_lines, b_lines, fromfile='a', tofile='b')
"""

from __future__ import annotations

import ctypes
import difflib as _difflib
from collections.abc import Sequence

# Re-export everything from Python's difflib
from difflib import (  # noqa: F401
    Differ,
    HtmlDiff,
    SequenceMatcher,
    context_diff,
    get_close_matches,
    ndiff,
    restore,
)

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 50  # Use Go for diffs with > 50 lines
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_diff_unified.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),  # aLines
            ctypes.c_int,                      # aCount
            ctypes.POINTER(ctypes.c_char_p),  # bLines
            ctypes.c_int,                      # bCount
            ctypes.c_char_p,                   # fromFile
            ctypes.c_char_p,                   # toFile
            ctypes.c_int,                      # contextLines
            ctypes.POINTER(ctypes.c_int),      # outLen
        ]
        lib.goated_diff_unified.restype = ctypes.c_char_p
        _lib_setup = True
    except Exception:
        pass


def unified_diff(
    a: Sequence[str],
    b: Sequence[str],
    fromfile: str = "",
    tofile: str = "",
    fromfiledate: str = "",
    tofiledate: str = "",
    n: int = 3,
    lineterm: str = "\n",
) -> list[str]:
    """Generate unified diff. Go-accelerated for large inputs.

    Unlike stdlib which returns a generator, this returns a list for
    Go batch processing. The result is compatible with list(difflib.unified_diff(...)).
    """
    a_list = list(a)
    b_list = list(b)

    if len(a_list) + len(b_list) < _GO_THRESHOLD or not _USE_GO_LIB:
        return list(_difflib.unified_diff(
            a_list, b_list, fromfile=fromfile, tofile=tofile,
            fromfiledate=fromfiledate, tofiledate=tofiledate,
            n=n, lineterm=lineterm,
        ))

    # filedate not supported in Go path; fall back if used
    if fromfiledate or tofiledate:
        return list(_difflib.unified_diff(
            a_list, b_list, fromfile=fromfile, tofile=tofile,
            fromfiledate=fromfiledate, tofiledate=tofiledate,
            n=n, lineterm=lineterm,
        ))

    # Prefer cffi
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi

            a_encoded = [line.encode("utf-8") for line in a_list]
            b_encoded = [line.encode("utf-8") for line in b_list]
            a_arr = _cffi_ffi.new("char*[]", [_cffi_ffi.new("char[]", s) for s in a_encoded])
            b_arr = _cffi_ffi.new("char*[]", [_cffi_ffi.new("char[]", s) for s in b_encoded])
            out_len = _cffi_ffi.new("int*")

            result = cffi_lib.goated_diff_unified(
                a_arr, len(a_list), b_arr, len(b_list),
                fromfile.encode("utf-8"), tofile.encode("utf-8"),
                n, out_len,
            )
            if result:
                text = _cffi_ffi.string(result).decode("utf-8")
                if text:
                    return text.split("\n")
                return []
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            a_encoded = [line.encode("utf-8") for line in a_list]
            b_encoded = [line.encode("utf-8") for line in b_list]
            a_arr = (ctypes.c_char_p * len(a_list))(*a_encoded)
            b_arr = (ctypes.c_char_p * len(b_list))(*b_encoded)
            out_len = ctypes.c_int()

            result = lib.goated_diff_unified(
                a_arr, len(a_list), b_arr, len(b_list),
                fromfile.encode("utf-8"), tofile.encode("utf-8"),
                n, ctypes.byref(out_len),
            )
            if result:
                text = result.decode("utf-8")
                if text:
                    return text.split("\n")
                return []
        except Exception:
            pass

    return list(_difflib.unified_diff(
        a_list, b_list, fromfile=fromfile, tofile=tofile,
        n=n, lineterm=lineterm,
    ))


__all__ = [
    "unified_diff",
    "context_diff",
    "ndiff",
    "restore",
    "Differ",
    "HtmlDiff",
    "SequenceMatcher",
    "get_close_matches",
]
