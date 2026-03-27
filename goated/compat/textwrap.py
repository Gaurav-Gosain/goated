"""Drop-in replacement for Python's textwrap module, backed by Go FFI.

Uses Go FFI for fill/wrap on large text inputs.
Falls back to Python for dedent, indent, shorten, and small inputs.

Usage:
    from goated.compat import textwrap
    wrapped = textwrap.fill("long text ...", width=70)
    lines = textwrap.wrap("long text ...", width=70)
"""

from __future__ import annotations

import ctypes
import textwrap as _textwrap

# Re-export everything from Python's textwrap
from textwrap import (  # noqa: F401
    TextWrapper,
    dedent,
    indent,
    shorten,
)

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 512  # Use Go for text > 512 chars
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_textwrap_fill.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.goated_textwrap_fill.restype = ctypes.c_char_p
        lib.goated_textwrap_wrap.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.goated_textwrap_wrap.restype = ctypes.c_uint64  # handle
        lib.goated_slice_string_len.argtypes = [ctypes.c_uint64]
        lib.goated_slice_string_len.restype = ctypes.c_int64
        lib.goated_slice_string_get.argtypes = [ctypes.c_uint64, ctypes.c_int64]
        lib.goated_slice_string_get.restype = ctypes.c_char_p
        lib.goated_handle_delete.argtypes = [ctypes.c_uint64]
        lib.goated_handle_delete.restype = None
        _lib_setup = True
    except Exception:
        pass


def fill(text: str, width: int = 70, **kwargs: object) -> str:
    """Fill a single paragraph of text. Go-accelerated for large inputs.

    Extra kwargs (e.g. initial_indent) fall back to Python.
    """
    if kwargs or len(text) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _textwrap.fill(text, width=width, **kwargs)

    # Prefer cffi
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi

            result = cffi_lib.goated_textwrap_fill(text.encode("utf-8"), width)
            if result:
                return _cffi_ffi.string(result).decode("utf-8")
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            result = lib.goated_textwrap_fill(text.encode("utf-8"), width)
            if result:
                return result.decode("utf-8")
        except Exception:
            pass

    return _textwrap.fill(text, width=width)


def wrap(text: str, width: int = 70, **kwargs: object) -> list[str]:
    """Wrap a single paragraph of text. Go-accelerated for large inputs.

    Extra kwargs (e.g. initial_indent) fall back to Python.
    """
    if kwargs or len(text) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _textwrap.wrap(text, width=width, **kwargs)

    # Prefer cffi
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi

            handle = cffi_lib.goated_textwrap_wrap(text.encode("utf-8"), width)
            if handle:
                try:
                    n = cffi_lib.goated_slice_string_len(handle)
                    lines = []
                    for i in range(n):
                        s = cffi_lib.goated_slice_string_get(handle, i)
                        lines.append(_cffi_ffi.string(s).decode("utf-8") if s else "")
                    return lines
                finally:
                    cffi_lib.goated_handle_delete(handle)
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            handle = lib.goated_textwrap_wrap(text.encode("utf-8"), width)
            if handle:
                try:
                    n = lib.goated_slice_string_len(handle)
                    lines = []
                    for i in range(n):
                        s = lib.goated_slice_string_get(handle, i)
                        lines.append(s.decode("utf-8") if s else "")
                    return lines
                finally:
                    lib.goated_handle_delete(handle)
        except Exception:
            pass

    return _textwrap.wrap(text, width=width)


__all__ = [
    "fill",
    "wrap",
    "dedent",
    "indent",
    "shorten",
    "TextWrapper",
]
