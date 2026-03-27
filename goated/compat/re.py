r"""Drop-in replacement for Python's re module, backed by Go's regexp (RE2).

Uses Go FFI for pattern compilation and matching when the pattern is
RE2-compatible (no backreferences, lookahead, lookbehind). Falls back to
Python's re module for unsupported features or when Go library is unavailable.

Usage:
    from goated.compat import re

    pattern = re.compile(r'\d+')
    match = pattern.search('hello 123 world')
    matches = re.findall(r'\w+', 'hello world')
"""

from __future__ import annotations

# template was removed in Python 3.14
import contextlib
import ctypes
import re as _re

# Re-export everything from Python's re module that we do not override
from re import (  # noqa: F401
    ASCII,
    DEBUG,
    DOTALL,
    IGNORECASE,
    LOCALE,
    MULTILINE,
    UNICODE,
    VERBOSE,
    A,
    I,
    L,
    M,
    Match,
    Pattern,
    S,
    U,
    X,
    error,
    escape,
    purge,
)
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

with contextlib.suppress(ImportError):
    from re import template  # type: ignore[attr-defined]  # noqa: F401

# NOFLAG was added in Python 3.11
try:
    from re import NOFLAG  # type: ignore[attr-defined]
except ImportError:
    NOFLAG = 0

# Patterns that need PCRE features not supported by RE2
import re as _re_mod

_PCRE_ONLY_FEATURES = _re_mod.compile(
    r"(?:"
    r"\\[0-9]"  # backreferences \1, \2, ...
    r"|"
    r"\(\?<[!=]"  # lookbehind (?<=...) (?<!...)
    r"|"
    r"\(\?[!=]"  # lookahead (?=...) (?!...)
    r"|"
    r"\(\?P=[a-zA-Z]"  # named backreference (?P=name)
    r"|"
    r"\(\?\("  # conditional patterns (?(id)yes|no)
    r"|"
    r"\(\?#"  # comment groups
    r")"
)

_lib_setup = False
_fn_configured: set[str] = set()


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_regexp_compile.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_regexp_compile.restype = ctypes.c_uint64

        lib.goated_regexp_match_string.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
        lib.goated_regexp_match_string.restype = ctypes.c_bool

        lib.goated_regexp_find_string.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
        lib.goated_regexp_find_string.restype = ctypes.c_char_p

        lib.goated_regexp_find_all_string.argtypes = [
            ctypes.c_uint64,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        lib.goated_regexp_find_all_string.restype = ctypes.c_uint64

        lib.goated_regexp_replace_all_string.argtypes = [
            ctypes.c_uint64,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        lib.goated_regexp_replace_all_string.restype = ctypes.c_char_p

        lib.goated_regexp_split.argtypes = [
            ctypes.c_uint64,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        lib.goated_regexp_split.restype = ctypes.c_uint64

        lib.goated_handle_delete.argtypes = [ctypes.c_uint64]
        lib.goated_handle_delete.restype = None

        lib.goated_slice_string_len.argtypes = [ctypes.c_uint64]
        lib.goated_slice_string_len.restype = ctypes.c_int64

        lib.goated_slice_string_get.argtypes = [ctypes.c_uint64, ctypes.c_int64]
        lib.goated_slice_string_get.restype = ctypes.c_char_p

        lib.goated_free_string.argtypes = [ctypes.c_char_p]
        lib.goated_free_string.restype = None

        _lib_setup = True
    except Exception:
        pass


def _pattern_needs_pcre(pattern: str) -> bool:
    """Check if the pattern uses PCRE features not supported by Go RE2."""
    return _PCRE_ONLY_FEATURES.search(pattern) is not None


def _has_flags(flags: int) -> bool:
    """Check if flags are set that require Python's re."""
    # Go RE2 does not support LOCALE or DEBUG
    return bool(flags & (_re.LOCALE | _re.DEBUG))


def _get_go_handle_strings(handle: int) -> list[str]:
    """Extract string slice from Go handle, then delete the handle."""
    lib = get_lib().lib
    length = lib.goated_slice_string_len(ctypes.c_uint64(handle))
    result = []
    for i in range(length):
        s = lib.goated_slice_string_get(ctypes.c_uint64(handle), ctypes.c_int64(i))
        result.append(s.decode("utf-8") if s else "")
    lib.goated_handle_delete(ctypes.c_uint64(handle))
    return result


class _GoPattern:
    """Wraps a Go compiled regexp with fallback to Python re.Pattern.

    Provides the same interface as re.Pattern but uses Go RE2 for matching
    operations.
    """

    def __init__(self, pattern: str, flags: int = 0) -> None:
        self._pattern_str = pattern
        self._flags = flags
        self._py_pattern: _re.Pattern[str] = _re.compile(pattern, flags)
        self._go_handle: int = 0
        self._use_go = False

        if _USE_GO_LIB and not _pattern_needs_pcre(pattern) and not _has_flags(flags):
            _setup_lib()
            if _lib_setup:
                try:
                    lib = get_lib().lib
                    err_out = ctypes.c_char_p()
                    # Apply inline flags for Go RE2
                    go_pattern = pattern
                    if flags & _re.IGNORECASE:
                        go_pattern = "(?i)" + go_pattern
                    if flags & _re.MULTILINE:
                        go_pattern = "(?m)" + go_pattern
                    if flags & _re.DOTALL:
                        go_pattern = "(?s)" + go_pattern

                    handle = lib.goated_regexp_compile(
                        go_pattern.encode("utf-8"),
                        ctypes.byref(err_out),
                    )
                    if handle and not err_out.value:
                        self._go_handle = handle
                        self._use_go = True
                except Exception:
                    pass

    def __del__(self) -> None:
        if self._go_handle and _USE_GO_LIB:
            try:
                lib = get_lib().lib
                lib.goated_handle_delete(ctypes.c_uint64(self._go_handle))
            except Exception:
                pass

    @property
    def pattern(self) -> str:
        return self._pattern_str

    @property
    def flags(self) -> int:
        return self._flags

    @property
    def groups(self) -> int:
        return self._py_pattern.groups

    @property
    def groupindex(self) -> dict[str, int]:
        return dict(self._py_pattern.groupindex)

    def search(self, string: str, pos: int = 0, endpos: int | None = None) -> Match[str] | None:
        if endpos is not None:
            return self._py_pattern.search(string, pos, endpos)
        return self._py_pattern.search(string, pos)

    def match(self, string: str, pos: int = 0, endpos: int | None = None) -> Match[str] | None:
        if endpos is not None:
            return self._py_pattern.match(string, pos, endpos)
        return self._py_pattern.match(string, pos)

    def fullmatch(self, string: str, pos: int = 0, endpos: int | None = None) -> Match[str] | None:
        if endpos is not None:
            return self._py_pattern.fullmatch(string, pos, endpos)
        return self._py_pattern.fullmatch(string, pos)

    def findall(self, string: str, pos: int = 0, endpos: int | None = None) -> list[Any]:
        # Use Go for simple findall (no pos/endpos, no groups)
        if self._use_go and pos == 0 and endpos is None and self._py_pattern.groups == 0:
            try:
                lib = get_lib().lib
                handle = lib.goated_regexp_find_all_string(
                    ctypes.c_uint64(self._go_handle),
                    string.encode("utf-8"),
                    ctypes.c_int(-1),
                )
                if handle:
                    return _get_go_handle_strings(handle)
            except Exception:
                pass
        if endpos is not None:
            return self._py_pattern.findall(string, pos, endpos)
        return self._py_pattern.findall(string, pos)

    def finditer(self, string: str, pos: int = 0, endpos: int | None = None) -> Any:
        if endpos is not None:
            return self._py_pattern.finditer(string, pos, endpos)
        return self._py_pattern.finditer(string, pos)

    def sub(self, repl: str | Any, string: str, count: int = 0) -> str:
        if self._use_go and count == 0 and isinstance(repl, str):
            try:
                lib = get_lib().lib
                result = lib.goated_regexp_replace_all_string(
                    ctypes.c_uint64(self._go_handle),
                    string.encode("utf-8"),
                    repl.encode("utf-8"),
                )
                if result:
                    val = result.decode("utf-8")
                    lib.goated_free_string(result)
                    return val
            except Exception:
                pass
        return self._py_pattern.sub(repl, string, count)

    def subn(self, repl: str | Any, string: str, count: int = 0) -> tuple[str, int]:
        return self._py_pattern.subn(repl, string, count)

    def split(self, string: str, maxsplit: int = 0) -> list[str]:
        if self._use_go and self._py_pattern.groups == 0:
            try:
                lib = get_lib().lib
                n = maxsplit + 1 if maxsplit > 0 else -1
                handle = lib.goated_regexp_split(
                    ctypes.c_uint64(self._go_handle),
                    string.encode("utf-8"),
                    ctypes.c_int(n),
                )
                if handle:
                    return _get_go_handle_strings(handle)
            except Exception:
                pass
        return self._py_pattern.split(string, maxsplit)

    def __repr__(self) -> str:
        return f"goated.compat.re.compile({self._pattern_str!r})"


def compile(pattern: str, flags: int = 0) -> _GoPattern | Pattern[str]:
    """Compile a regular expression pattern, returning a pattern object.

    Uses Go RE2 when the pattern is compatible; falls back to Python re.
    """
    if _USE_GO_LIB and not _pattern_needs_pcre(pattern) and not _has_flags(flags):
        return _GoPattern(pattern, flags)
    return _re.compile(pattern, flags)


def search(pattern: str, string: str, flags: int = 0) -> Match[str] | None:
    """Scan through string looking for a match to the pattern."""
    return _re.search(pattern, string, flags)


def match(pattern: str, string: str, flags: int = 0) -> Match[str] | None:
    """Try to apply the pattern at the start of the string."""
    return _re.match(pattern, string, flags)


def fullmatch(pattern: str, string: str, flags: int = 0) -> Match[str] | None:
    """Try to apply the pattern to all of the string."""
    return _re.fullmatch(pattern, string, flags)


def split(pattern: str, string: str, maxsplit: int = 0, flags: int = 0) -> list[str]:
    """Split the source string by the occurrences of the pattern."""
    return _re.split(pattern, string, maxsplit=maxsplit, flags=flags)


def findall(pattern: str, string: str, flags: int = 0) -> list[Any]:
    """Return a list of all non-overlapping matches in the string."""
    return _re.findall(pattern, string, flags)


def finditer(pattern: str, string: str, flags: int = 0) -> Any:
    """Return an iterator yielding match objects over non-overlapping matches."""
    return _re.finditer(pattern, string, flags)


def sub(pattern: str, repl: str | Any, string: str, count: int = 0, flags: int = 0) -> str:
    """Return the string obtained by replacing the leftmost occurrences of pattern."""
    return _re.sub(pattern, repl, string, count=count, flags=flags)


def subn(
    pattern: str,
    repl: str | Any,
    string: str,
    count: int = 0,
    flags: int = 0,
) -> tuple[str, int]:
    """Like sub(), but also return the number of substitutions made."""
    return _re.subn(pattern, repl, string, count=count, flags=flags)


__all__ = [
    # Functions
    "compile",
    "search",
    "match",
    "fullmatch",
    "split",
    "findall",
    "finditer",
    "sub",
    "subn",
    "escape",
    "purge",
    # Classes
    "Pattern",
    "Match",
    "error",
    # Flags
    "A",
    "ASCII",
    "DEBUG",
    "I",
    "IGNORECASE",
    "L",
    "LOCALE",
    "M",
    "MULTILINE",
    "S",
    "DOTALL",
    "X",
    "VERBOSE",
    "U",
    "UNICODE",
    "NOFLAG",
]
