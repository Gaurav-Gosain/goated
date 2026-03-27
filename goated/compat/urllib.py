"""Drop-in replacement for urllib.parse functions, backed by Go's net/url.

urllib.parse.quote/unquote are pure Python - Go provides 8-10x speedup.
Uses cffi API mode for fastest FFI (compiled C extension).

Usage:
    from goated.compat.urllib import quote, unquote, urlencode
"""

from __future__ import annotations

import ctypes
from urllib.parse import (  # noqa: F401
    DefragResult,
    ParseResult,
    SplitResult,
    parse_qs,
    parse_qsl,
    splitquery,
    urlencode,
    urljoin,
    urlparse,
    urlsplit,
    urlunparse,
    urlunsplit,
)
from urllib.parse import quote as _py_quote
from urllib.parse import quote_plus as _py_quote_plus
from urllib.parse import unquote as _py_unquote
from urllib.parse import unquote_plus as _py_unquote_plus

from goated._core import _USE_GO_LIB, get_cffi_lib, get_lib

_GO_THRESHOLD = 64  # URL functions are pure Python, Go wins even at small sizes
_lib_setup = False
_use_cffi = False


def _setup_lib() -> None:
    global _lib_setup, _use_cffi
    if _lib_setup or not _USE_GO_LIB:
        return

    # Prefer cffi API mode (fastest)
    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        _use_cffi = True
        _lib_setup = True
        return

    # Fallback to ctypes
    try:
        lib = get_lib().lib
        lib.goated_url_query_escape.argtypes = [ctypes.c_char_p]
        lib.goated_url_query_escape.restype = ctypes.c_char_p
        lib.goated_url_query_unescape.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_url_query_unescape.restype = ctypes.c_char_p
        lib.goated_url_path_escape.argtypes = [ctypes.c_char_p]
        lib.goated_url_path_escape.restype = ctypes.c_char_p
        lib.goated_url_path_unescape.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_url_path_unescape.restype = ctypes.c_char_p
        _lib_setup = True
    except Exception:
        pass


def quote(
    string: str,
    safe: str = "/",
    encoding: str | None = None,
    errors: str | None = None,
) -> str:
    """URL-encode a string. Go-accelerated (8-10x faster than urllib.parse).

    Note: Go's QueryEscape percent-encodes everything including '/'.
    We use Go for the common case (safe='/') and fall back for custom safe chars.
    """
    if encoding is not None or errors is not None or safe != "/":
        return _py_quote(string, safe=safe, encoding=encoding, errors=errors)

    if not _USE_GO_LIB or len(string) < _GO_THRESHOLD:
        return _py_quote(string, safe=safe)

    _setup_lib()
    if not _lib_setup:
        return _py_quote(string, safe=safe)

    try:
        encoded = string.encode("utf-8")
        if _use_cffi:
            cffi_lib = get_cffi_lib()
            result = cffi_lib.goated_url_path_escape(encoded)
            if result:
                from goated._core import _cffi_ffi

                return _cffi_ffi.string(result).decode("utf-8")
        else:
            lib = get_lib().lib
            result = lib.goated_url_path_escape(encoded)
            if result:
                return result.decode("utf-8")
    except Exception:
        pass
    return _py_quote(string, safe=safe)


def quote_plus(
    string: str,
    safe: str = "",
    encoding: str | None = None,
    errors: str | None = None,
) -> str:
    """Like quote() but also replaces spaces with +. Go-accelerated."""
    if encoding is not None or errors is not None or safe:
        return _py_quote_plus(string, safe=safe, encoding=encoding, errors=errors)

    if not _USE_GO_LIB or len(string) < _GO_THRESHOLD:
        return _py_quote_plus(string, safe=safe)

    _setup_lib()
    if not _lib_setup:
        return _py_quote_plus(string, safe=safe)

    try:
        encoded = string.encode("utf-8")
        if _use_cffi:
            cffi_lib = get_cffi_lib()
            result = cffi_lib.goated_url_query_escape(encoded)
            if result:
                from goated._core import _cffi_ffi

                return _cffi_ffi.string(result).decode("utf-8")
        else:
            lib = get_lib().lib
            result = lib.goated_url_query_escape(encoded)
            if result:
                return result.decode("utf-8")
    except Exception:
        pass
    return _py_quote_plus(string, safe=safe)


def unquote(string: str, encoding: str = "utf-8", errors: str = "replace") -> str:
    """URL-decode a string. Go-accelerated (8-10x faster than urllib.parse)."""
    if encoding != "utf-8" or errors != "replace":
        return _py_unquote(string, encoding=encoding, errors=errors)

    if not _USE_GO_LIB or len(string) < _GO_THRESHOLD:
        return _py_unquote(string, encoding=encoding, errors=errors)

    _setup_lib()
    if not _lib_setup:
        return _py_unquote(string, encoding=encoding, errors=errors)

    try:
        encoded = string.encode("utf-8")
        if _use_cffi:
            cffi_lib = get_cffi_lib()
            from goated._core import _cffi_ffi

            err_out = _cffi_ffi.new("char**")
            result = cffi_lib.goated_url_query_unescape(encoded, err_out)
            if result and not err_out[0]:
                return _cffi_ffi.string(result).decode("utf-8")
        else:
            lib = get_lib().lib
            err_out = ctypes.c_char_p()
            result = lib.goated_url_query_unescape(encoded, ctypes.byref(err_out))
            if result and not err_out.value:
                return result.decode("utf-8")
    except Exception:
        pass
    return _py_unquote(string, encoding=encoding, errors=errors)


def unquote_plus(string: str, encoding: str = "utf-8", errors: str = "replace") -> str:
    """Like unquote() but also replaces + with spaces. Go-accelerated."""
    # Go's QueryUnescape handles + -> space
    if encoding != "utf-8" or errors != "replace":
        return _py_unquote_plus(string, encoding=encoding, errors=errors)

    if not _USE_GO_LIB or len(string) < _GO_THRESHOLD:
        return _py_unquote_plus(string, encoding=encoding, errors=errors)

    return unquote(string.replace("+", "%20"), encoding=encoding, errors=errors)


__all__ = [
    "quote",
    "quote_plus",
    "unquote",
    "unquote_plus",
    "urlencode",
    "urljoin",
    "urlparse",
    "urlsplit",
    "urlunparse",
    "urlunsplit",
    "parse_qs",
    "parse_qsl",
    "ParseResult",
    "SplitResult",
    "DefragResult",
]
