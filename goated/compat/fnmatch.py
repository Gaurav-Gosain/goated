"""Drop-in replacement for Python's fnmatch module, backed by Go's filepath.Match.

Uses Go FFI for pattern matching, especially effective for batch filtering.
Falls back to Python for translate().

Usage:
    from goated.compat import fnmatch
    fnmatch.fnmatch("foo.py", "*.py")  # True
    fnmatch.filter(["a.py", "b.txt", "c.py"], "*.py")  # ["a.py", "c.py"]
"""

from __future__ import annotations

import ctypes
import fnmatch as _fnmatch
from collections.abc import Sequence

# Re-export translate from Python's fnmatch
from fnmatch import translate  # noqa: F401

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 10  # Use Go for filter() with > 10 names
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_fnmatch.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.goated_fnmatch.restype = ctypes.c_bool
        lib.goated_batch_fnmatch.argtypes = [
            ctypes.c_char_p,  # pattern
            ctypes.POINTER(ctypes.c_char_p),  # names
            ctypes.c_int,  # count
            ctypes.POINTER(ctypes.c_bool),  # results
        ]
        lib.goated_batch_fnmatch.restype = None
        lib.goated_fnmatch_filter.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),  # names
            ctypes.c_int,  # count
            ctypes.c_char_p,  # pattern
        ]
        lib.goated_fnmatch_filter.restype = ctypes.c_uint64  # handle
        lib.goated_slice_string_len.argtypes = [ctypes.c_uint64]
        lib.goated_slice_string_len.restype = ctypes.c_int64
        lib.goated_slice_string_get.argtypes = [ctypes.c_uint64, ctypes.c_int64]
        lib.goated_slice_string_get.restype = ctypes.c_char_p
        lib.goated_handle_delete.argtypes = [ctypes.c_uint64]
        lib.goated_handle_delete.restype = None
        _lib_setup = True
    except Exception:
        pass


def fnmatch(name: str, pat: str) -> bool:
    """Test whether name matches pattern. Go-accelerated.

    Note: Go's filepath.Match has slightly different semantics from Python's
    fnmatch for some edge cases. Falls back to Python on Go errors.
    """
    if not _USE_GO_LIB:
        return _fnmatch.fnmatch(name, pat)

    # Prefer cffi
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            return bool(
                cffi_lib.goated_fnmatch(
                    pat.encode("utf-8"),
                    name.encode("utf-8"),
                )
            )
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            return bool(
                lib.goated_fnmatch(
                    pat.encode("utf-8"),
                    name.encode("utf-8"),
                )
            )
        except Exception:
            pass

    return _fnmatch.fnmatch(name, pat)


def fnmatchcase(name: str, pat: str) -> bool:
    """Test whether name matches pattern, case-sensitive.

    Falls back to Python since Go's filepath.Match is already case-sensitive.
    """
    return _fnmatch.fnmatchcase(name, pat)


def filter(names: Sequence[str], pat: str) -> list[str]:
    """Filter names by pattern. Go-accelerated for large lists."""
    names_list = list(names)

    if len(names_list) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _fnmatch.filter(names_list, pat)

    # Prefer cffi for batch
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi

            encoded = [n.encode("utf-8") for n in names_list]
            names_arr = _cffi_ffi.new("char*[]", [_cffi_ffi.new("char[]", s) for s in encoded])
            results = _cffi_ffi.new("_Bool[]", len(names_list))
            cffi_lib.goated_batch_fnmatch(
                pat.encode("utf-8"),
                names_arr,
                len(names_list),
                results,
            )
            return [n for n, m in zip(names_list, results, strict=False) if m]
        except Exception:
            pass

    # Fallback to ctypes batch
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            encoded = [n.encode("utf-8") for n in names_list]
            names_arr = (ctypes.c_char_p * len(names_list))(*encoded)
            results = (ctypes.c_bool * len(names_list))()
            lib.goated_batch_fnmatch(
                pat.encode("utf-8"),
                names_arr,
                len(names_list),
                results,
            )
            return [n for n, m in zip(names_list, results, strict=False) if m]
        except Exception:
            pass

    return _fnmatch.filter(names_list, pat)


__all__ = [
    "fnmatch",
    "fnmatchcase",
    "filter",
    "translate",
]
