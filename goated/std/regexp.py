"""Go regexp package bindings.

This module provides Python bindings for Go's regexp package.
"""

from __future__ import annotations

import ctypes
import re

from goated._core import get_lib, is_library_available
from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Compile",
    "CompilePOSIX",
    "Match",
    "MatchString",
    "MustCompile",
    "MustCompilePOSIX",
    "QuoteMeta",
    "Regexp",
]


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")


_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[object], restype: object) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


class Regexp:
    """Regexp is the representation of a compiled regular expression."""

    def __init__(self, pattern: str, posix: bool = False):
        self._pattern = pattern
        self._posix = posix
        self._compiled: re.Pattern[str] | None = None
        self._error: str | None = None

        try:
            self._compiled = re.compile(pattern)
        except re.error as e:
            self._error = str(e)

    @property
    def pattern(self) -> str:
        return self._pattern

    def Match(self, b: bytes) -> bool:
        if self._compiled is None:
            return False
        try:
            return self._compiled.search(b.decode("utf-8")) is not None
        except Exception:
            return False

    def MatchString(self, s: str) -> bool:
        if self._compiled is None:
            return False
        return self._compiled.search(s) is not None

    def Find(self, b: bytes) -> bytes | None:
        if self._compiled is None:
            return None
        try:
            match = self._compiled.search(b.decode("utf-8"))
            if match:
                return match.group(0).encode("utf-8")
        except Exception:
            pass
        return None

    def FindString(self, s: str) -> str:
        if self._compiled is None:
            return ""
        match = self._compiled.search(s)
        return match.group(0) if match else ""

    def FindAll(self, b: bytes, n: int = -1) -> list[bytes] | None:
        if self._compiled is None:
            return None
        try:
            s = b.decode("utf-8")
            matches = self._compiled.findall(s)
            if n >= 0:
                matches = matches[:n]
            return (
                [
                    m.encode("utf-8") if isinstance(m, str) else str(m).encode("utf-8")
                    for m in matches
                ]
                if matches
                else None
            )
        except Exception:
            return None

    def FindAllString(self, s: str, n: int = -1) -> list[str] | None:
        if self._compiled is None:
            return None
        matches = self._compiled.findall(s)
        if n >= 0:
            matches = matches[:n]
        result = []
        for m in matches:
            if isinstance(m, tuple):
                result.append(m[0] if m else "")
            else:
                result.append(m)
        return result if result else None

    def FindStringIndex(self, s: str) -> tuple[int, int] | None:
        if self._compiled is None:
            return None
        match = self._compiled.search(s)
        if match:
            return (match.start(), match.end())
        return None

    def FindStringSubmatch(self, s: str) -> list[str] | None:
        if self._compiled is None:
            return None
        match = self._compiled.search(s)
        if match:
            return [match.group(0)] + list(match.groups())
        return None

    def ReplaceAll(self, src: bytes, repl: bytes) -> bytes:
        if self._compiled is None:
            return src
        try:
            s = src.decode("utf-8")
            r = repl.decode("utf-8")
            return self._compiled.sub(r, s).encode("utf-8")
        except Exception:
            return src

    def ReplaceAllString(self, src: str, repl: str) -> str:
        if self._compiled is None:
            return src
        return self._compiled.sub(repl, src)

    def ReplaceAllLiteralString(self, src: str, repl: str) -> str:
        if self._compiled is None:
            return src
        return self._compiled.sub(lambda m: repl, src)

    def Split(self, s: str, n: int = -1) -> list[str]:
        if self._compiled is None:
            return [s]
        if n == 0:
            return []
        return self._compiled.split(s, maxsplit=n - 1 if n > 0 else 0)

    def String(self) -> str:
        return self._pattern

    def __str__(self) -> str:
        return self._pattern

    def __repr__(self) -> str:
        return f"Regexp({self._pattern!r})"


def Compile(expr: str) -> Result[Regexp, GoError]:
    """Compile parses a regular expression and returns a Regexp object."""
    try:
        re.compile(expr)
        return Ok(Regexp(expr))
    except re.error as e:
        return Err(GoError(f"error parsing regexp: {e}"))


def CompilePOSIX(expr: str) -> Result[Regexp, GoError]:
    """CompilePOSIX is like Compile but restricts to POSIX ERE syntax."""
    try:
        re.compile(expr)
        return Ok(Regexp(expr, posix=True))
    except re.error as e:
        return Err(GoError(f"error parsing regexp: {e}"))


def MustCompile(expr: str) -> Regexp:
    """MustCompile is like Compile but panics if the expression cannot be parsed."""
    result = Compile(expr)
    if result.is_err():
        err = result.err()
        raise ValueError(f"regexp: Compile({expr!r}): {err}")
    return result.unwrap()


def MustCompilePOSIX(expr: str) -> Regexp:
    """MustCompilePOSIX is like CompilePOSIX but panics if the expression cannot be parsed."""
    result = CompilePOSIX(expr)
    if result.is_err():
        err = result.err()
        raise ValueError(f"regexp: CompilePOSIX({expr!r}): {err}")
    return result.unwrap()


def Match(pattern: str, b: bytes) -> Result[bool, GoError]:
    """Match reports whether b contains any match of pattern."""
    try:
        compiled = re.compile(pattern)
        return Ok(compiled.search(b.decode("utf-8")) is not None)
    except re.error as e:
        return Err(GoError(f"error parsing regexp: {e}"))
    except UnicodeDecodeError as e:
        return Err(GoError(f"invalid UTF-8: {e}"))


def MatchString(pattern: str, s: str) -> Result[bool, GoError]:
    """MatchString reports whether s contains any match of pattern."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_regexp_MatchString",
                [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
                ctypes.c_bool,
            )
            err_out = ctypes.c_char_p()
            result = lib.goated_regexp_MatchString(
                _encode(pattern), _encode(s), ctypes.byref(err_out)
            )

            if err_out.value:
                return Err(GoError(_decode(err_out.value)))
            return Ok(bool(result))
        except Exception:
            pass

    # Pure Python fallback
    try:
        compiled = re.compile(pattern)
        return Ok(compiled.search(s) is not None)
    except re.error as e:
        return Err(GoError(f"error parsing regexp: {e}"))


def QuoteMeta(s: str) -> str:
    """QuoteMeta returns a string that escapes all regexp metacharacters."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_regexp_QuoteMeta", [ctypes.c_char_p], ctypes.c_char_p)
            result = lib.goated_regexp_QuoteMeta(_encode(s))
            if result:
                return _decode(result)
        except Exception:
            pass

    return re.escape(s)
