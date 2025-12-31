"""Go utf8 package bindings.

This module provides Python bindings for Go's unicode/utf8 package.
"""

from __future__ import annotations

import ctypes

from goated._core import get_lib, is_library_available

__all__ = [
    "DecodeLastRune",
    "DecodeLastRuneInString",
    "DecodeRune",
    "DecodeRuneInString",
    "EncodeRune",
    "FullRune",
    "FullRuneInString",
    "RuneCount",
    "RuneCountInString",
    "RuneLen",
    "RuneStart",
    "Valid",
    "ValidRune",
    "ValidString",
    # Constants
    "RuneError",
    "RuneSelf",
    "MaxRune",
    "UTFMax",
]

# Constants
RuneError = "\ufffd"  # The "error" rune or "Unicode replacement character"
RuneSelf = 0x80  # Characters below RuneSelf are represented as themselves
MaxRune = 0x10FFFF  # Maximum valid Unicode code point
UTFMax = 4  # Maximum number of bytes of a UTF-8 encoded character


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")


def _get_rune(r: str | int) -> int:
    """Convert a string character to its code point (rune)."""
    if isinstance(r, int):
        return r
    if isinstance(r, str) and len(r) > 0:
        return ord(r[0])
    return 0


_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[type], restype: type) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


def DecodeLastRune(p: bytes) -> tuple[str, int]:
    """DecodeLastRune unpacks the last UTF-8 encoding in p."""
    if not p:
        return RuneError, 0

    i = len(p) - 1
    while i > 0 and (p[i] & 0xC0) == 0x80:
        i -= 1
        if len(p) - i > UTFMax:
            return RuneError, 1

    try:
        s = p[i:].decode("utf-8")
        if s:
            return s[0], len(p) - i
    except UnicodeDecodeError:
        pass

    return RuneError, 1


def DecodeLastRuneInString(s: str) -> tuple[str, int]:
    """DecodeLastRuneInString is like DecodeLastRune but for strings."""
    if not s:
        return RuneError, 0

    last_char = s[-1]
    byte_len = len(last_char.encode("utf-8"))
    return last_char, byte_len


def DecodeRune(p: bytes) -> tuple[str, int]:
    """DecodeRune unpacks the first UTF-8 encoding in p."""
    if not p:
        return RuneError, 0

    for width in range(1, min(UTFMax + 1, len(p) + 1)):
        try:
            s = p[:width].decode("utf-8")
            if s:
                return s[0], width
        except UnicodeDecodeError:
            continue

    return RuneError, 1


def DecodeRuneInString(s: str) -> tuple[str, int]:
    """DecodeRuneInString is like DecodeRune but for strings."""
    if not s:
        return RuneError, 0

    first_char = s[0]
    byte_len = len(first_char.encode("utf-8"))
    return first_char, byte_len


def EncodeRune(p: bytearray, r: str | int) -> int:
    """EncodeRune writes the UTF-8 encoding of the rune into p."""
    rune = _get_rune(r)

    if rune < 0 or rune > MaxRune or (0xD800 <= rune <= 0xDFFF):
        rune = ord(RuneError)

    try:
        encoded = chr(rune).encode("utf-8")
        for i, b in enumerate(encoded):
            if i < len(p):
                p[i] = b
        return len(encoded)
    except (ValueError, OverflowError):
        encoded = RuneError.encode("utf-8")
        for i, b in enumerate(encoded):
            if i < len(p):
                p[i] = b
        return len(encoded)


def FullRune(p: bytes) -> bool:
    """FullRune reports whether p begins with a full UTF-8 encoding of a rune."""
    if not p:
        return False

    first_byte = p[0]
    if first_byte < 0x80 or first_byte < 0xC0:
        return True
    elif first_byte < 0xE0:
        expected = 2
    elif first_byte < 0xF0:
        expected = 3
    elif first_byte < 0xF8:
        expected = 4
    else:
        return True

    return len(p) >= expected


def FullRuneInString(s: str) -> bool:
    """FullRuneInString is like FullRune but for strings."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_utf8_FullRuneInString", [ctypes.c_char_p], ctypes.c_bool)
            return bool(lib.goated_utf8_FullRuneInString(_encode(s)))
        except Exception:
            pass

    return len(s) > 0


def RuneCount(p: bytes) -> int:
    """RuneCount returns the number of runes in p."""
    try:
        return len(p.decode("utf-8", errors="replace"))
    except Exception:
        return len(p)


def RuneCountInString(s: str) -> int:
    """RuneCountInString returns the number of runes in s."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib, "goated_utf8_RuneCountInString", [ctypes.c_char_p], ctypes.c_longlong
            )
            return int(lib.goated_utf8_RuneCountInString(_encode(s)))
        except Exception:
            pass

    return len(s)


def RuneLen(r: str | int) -> int:
    """RuneLen returns the number of bytes in the UTF-8 encoding of the rune."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_utf8_RuneLen", [ctypes.c_int], ctypes.c_longlong)
            return int(lib.goated_utf8_RuneLen(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune or (0xD800 <= rune <= 0xDFFF):
        return -1

    if rune < 0x80:
        return 1
    elif rune < 0x800:
        return 2
    elif rune < 0x10000:
        return 3
    else:
        return 4


def RuneStart(b: int) -> bool:
    """RuneStart reports whether b could be the first byte of an encoded rune."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_utf8_RuneStart", [ctypes.c_ubyte], ctypes.c_bool)
            return bool(lib.goated_utf8_RuneStart(b))
        except Exception:
            pass

    return (b & 0xC0) != 0x80


def Valid(p: bytes) -> bool:
    """Valid reports whether p consists entirely of valid UTF-8-encoded runes."""
    try:
        p.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def ValidRune(r: str | int) -> bool:
    """ValidRune reports whether r can be legally encoded as UTF-8."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_utf8_ValidRune", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_utf8_ValidRune(rune))
        except Exception:
            pass

    if rune < 0 or rune > MaxRune:
        return False
    return not 55296 <= rune <= 57343


def ValidString(s: str) -> bool:
    """ValidString reports whether s consists entirely of valid UTF-8-encoded runes."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_utf8_ValidString", [ctypes.c_char_p], ctypes.c_bool)
            return bool(lib.goated_utf8_ValidString(_encode(s)))
        except Exception:
            pass

    try:
        s.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False
