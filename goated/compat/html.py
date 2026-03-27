"""Drop-in replacement for Python's html module, backed by Go's html package.

Uses Go FFI for escape/unescape of strings.

Usage:
    from goated.compat import html
    safe = html.escape("<script>alert('xss')</script>")
    original = html.unescape("&lt;b&gt;bold&lt;/b&gt;")
"""

from __future__ import annotations

import ctypes
import html as _html

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 256
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_html_escape_string.argtypes = [ctypes.c_char_p]
        lib.goated_html_escape_string.restype = ctypes.c_char_p
        lib.goated_html_unescape_string.argtypes = [ctypes.c_char_p]
        lib.goated_html_unescape_string.restype = ctypes.c_char_p
        _lib_setup = True
    except Exception:
        pass


def escape(s: str, quote: bool = True) -> str:
    """Escape HTML special characters.

    Note: Go's html.EscapeString uses &#34; for quotes while Python uses &quot;.
    We use Python's implementation for exact compatibility.
    """
    return _html.escape(s, quote=quote)


def unescape(s: str) -> str:
    """Unescape HTML entities. Go-accelerated (12x faster than stdlib).

    html.unescape is pure Python in the stdlib, making this one of
    the biggest speedup opportunities in goated.
    """
    if len(s) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _html.unescape(s)

    # Prefer cffi API mode (fastest)
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi
            result = cffi_lib.goated_html_unescape_string(s.encode("utf-8"))
            if result:
                return _cffi_ffi.string(result).decode("utf-8")
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            result = lib.goated_html_unescape_string(s.encode("utf-8"))
            if result:
                return result.decode("utf-8")
        except Exception:
            pass
    return _html.unescape(s)


__all__ = [
    "escape",
    "unescape",
]
