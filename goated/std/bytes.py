"""Go bytes package bindings.

This module provides Python bindings for Go's bytes package for byte slice operations.

Example:
    >>> from goated.std import bytes as gobytes
    >>>
    >>> gobytes.Contains(b"hello", b"ell")
    True
    >>> gobytes.ToUpper(b"hello")
    b'HELLO'

"""

from __future__ import annotations

import ctypes

from goated._core import get_lib, is_library_available

__all__ = [
    "Contains",
    "ContainsAny",
    "ContainsRune",
    "Count",
    "Equal",
    "EqualFold",
    "Compare",
    "HasPrefix",
    "HasSuffix",
    "Index",
    "IndexAny",
    "IndexByte",
    "IndexRune",
    "LastIndex",
    "LastIndexAny",
    "LastIndexByte",
    "ToLower",
    "ToUpper",
    "ToTitle",
    "Title",
    "TrimSpace",
    "Trim",
    "TrimLeft",
    "TrimRight",
    "TrimPrefix",
    "TrimSuffix",
    "Repeat",
    "Replace",
    "ReplaceAll",
    "Split",
    "SplitN",
    "SplitAfter",
    "SplitAfterN",
    "Join",
    "Fields",
    "Clone",
]

_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[type], restype: type) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


def Contains(b: bytes, subslice: bytes) -> bool:
    """Reports whether subslice is within b."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_Contains",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_bool,
            )
            return bool(lib.goated_bytes_Contains(b, len(b), subslice, len(subslice)))
        except Exception:
            pass
    return subslice in b


def ContainsAny(b: bytes, chars: bytes) -> bool:
    """Reports whether any of the bytes in chars are within b."""
    return any(c in b for c in chars)


def ContainsRune(b: bytes, r: str | int) -> bool:
    """Reports whether the rune is contained in b."""
    if isinstance(r, int):
        try:
            r = chr(r)
        except (ValueError, OverflowError):
            return False
    return r.encode("utf-8") in b if r else False


def Count(s: bytes, sep: bytes) -> int:
    """Counts the number of non-overlapping instances of sep in s."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_Count",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_longlong,
            )
            return int(lib.goated_bytes_Count(s, len(s), sep, len(sep)))
        except Exception:
            pass

    if sep == b"":
        return len(s) + 1
    return s.count(sep)


def Equal(a: bytes, b: bytes) -> bool:
    """Reports whether a and b are the same length and contain the same bytes."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_Equal",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_bool,
            )
            return bool(lib.goated_bytes_Equal(a, len(a), b, len(b)))
        except Exception:
            pass
    return a == b


def EqualFold(s: bytes, t: bytes) -> bool:
    """Reports whether s and t, interpreted as UTF-8 strings, are equal under case-folding."""
    try:
        return s.decode("utf-8").casefold() == t.decode("utf-8").casefold()
    except UnicodeDecodeError:
        return s.lower() == t.lower()


def Compare(a: bytes, b: bytes) -> int:
    """Returns -1 if a < b, 0 if a == b, 1 if a > b."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_Compare",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_int,
            )
            return int(lib.goated_bytes_Compare(a, len(a), b, len(b)))
        except Exception:
            pass

    if a < b:
        return -1
    elif a > b:
        return 1
    return 0


def HasPrefix(s: bytes, prefix: bytes) -> bool:
    """Tests whether s begins with prefix."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_HasPrefix",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_bool,
            )
            return bool(lib.goated_bytes_HasPrefix(s, len(s), prefix, len(prefix)))
        except Exception:
            pass
    return s.startswith(prefix)


def HasSuffix(s: bytes, suffix: bytes) -> bool:
    """Tests whether s ends with suffix."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_HasSuffix",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_bool,
            )
            return bool(lib.goated_bytes_HasSuffix(s, len(s), suffix, len(suffix)))
        except Exception:
            pass
    return s.endswith(suffix)


def Index(s: bytes, sep: bytes) -> int:
    """Returns the index of the first instance of sep in s, or -1."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_Index",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_longlong,
            )
            return int(lib.goated_bytes_Index(s, len(s), sep, len(sep)))
        except Exception:
            pass
    return s.find(sep)


def IndexAny(s: bytes, chars: bytes) -> int:
    """Returns the index of the first instance of any byte from chars in s, or -1."""
    for i, b in enumerate(s):
        if b in chars:
            return i
    return -1


def IndexByte(s: bytes, c: int) -> int:
    """Returns the index of the first instance of c in s, or -1."""
    try:
        return s.index(bytes([c]))
    except ValueError:
        return -1


def IndexRune(s: bytes, r: str | int) -> int:
    """Returns the index of the first instance of the rune in s, or -1."""
    if isinstance(r, int):
        try:
            r = chr(r)
        except (ValueError, OverflowError):
            return -1
    encoded = r.encode("utf-8")
    return s.find(encoded)


def LastIndex(s: bytes, sep: bytes) -> int:
    """Returns the index of the last instance of sep in s, or -1."""
    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(
                lib,
                "goated_bytes_LastIndex",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong],
                ctypes.c_longlong,
            )
            return int(lib.goated_bytes_LastIndex(s, len(s), sep, len(sep)))
        except Exception:
            pass
    return s.rfind(sep)


def LastIndexAny(s: bytes, chars: bytes) -> int:
    """Returns the index of the last instance of any byte from chars in s, or -1."""
    for i in range(len(s) - 1, -1, -1):
        if s[i] in chars:
            return i
    return -1


def LastIndexByte(s: bytes, c: int) -> int:
    """Returns the index of the last instance of c in s, or -1."""
    # Direct iteration is faster than reversing the entire slice
    for i in range(len(s) - 1, -1, -1):
        if s[i] == c:
            return i
    return -1


def ToLower(s: bytes) -> bytes:
    """Returns s with all ASCII letters mapped to their lower case."""
    if is_library_available():
        try:
            lib = get_lib()
            out_len = ctypes.c_longlong()
            _configure_fn(
                lib,
                "goated_bytes_ToLower",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong)],
                ctypes.c_char_p,
            )
            result = lib.goated_bytes_ToLower(s, len(s), ctypes.byref(out_len))
            if result:
                return ctypes.string_at(result, out_len.value)
        except Exception:
            pass
    return s.lower()


def ToUpper(s: bytes) -> bytes:
    """Returns s with all ASCII letters mapped to their upper case."""
    if is_library_available():
        try:
            lib = get_lib()
            out_len = ctypes.c_longlong()
            _configure_fn(
                lib,
                "goated_bytes_ToUpper",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong)],
                ctypes.c_char_p,
            )
            result = lib.goated_bytes_ToUpper(s, len(s), ctypes.byref(out_len))
            if result:
                return ctypes.string_at(result, out_len.value)
        except Exception:
            pass
    return s.upper()


def ToTitle(s: bytes) -> bytes:
    """Returns s with all Unicode letters mapped to their title case."""
    try:
        return s.decode("utf-8").title().encode("utf-8")
    except UnicodeDecodeError:
        return s.title()


def Title(s: bytes) -> bytes:
    """Returns s with all Unicode letters that begin words mapped to their title case.
    Deprecated: Use ToTitle instead.
    """
    return ToTitle(s)


def TrimSpace(s: bytes) -> bytes:
    """Returns s with all leading and trailing whitespace removed."""
    if is_library_available():
        try:
            lib = get_lib()
            out_len = ctypes.c_longlong()
            _configure_fn(
                lib,
                "goated_bytes_TrimSpace",
                [ctypes.c_char_p, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong)],
                ctypes.c_char_p,
            )
            result = lib.goated_bytes_TrimSpace(s, len(s), ctypes.byref(out_len))
            if result:
                return ctypes.string_at(result, out_len.value)
        except Exception:
            pass
    return s.strip()


def Trim(s: bytes, cutset: bytes) -> bytes:
    """Returns s with all leading and trailing bytes in cutset removed."""
    return s.strip(cutset)


def TrimLeft(s: bytes, cutset: bytes) -> bytes:
    """Returns s with all leading bytes in cutset removed."""
    return s.lstrip(cutset)


def TrimRight(s: bytes, cutset: bytes) -> bytes:
    """Returns s with all trailing bytes in cutset removed."""
    return s.rstrip(cutset)


def TrimPrefix(s: bytes, prefix: bytes) -> bytes:
    """Returns s without the leading prefix, or s unchanged if prefix not present."""
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def TrimSuffix(s: bytes, suffix: bytes) -> bytes:
    """Returns s without the trailing suffix, or s unchanged if suffix not present."""
    if suffix and s.endswith(suffix):
        return s[: -len(suffix)]
    return s


def Repeat(b: bytes, count: int) -> bytes:
    """Returns a new byte slice consisting of count copies of b."""
    if is_library_available():
        try:
            lib = get_lib()
            out_len = ctypes.c_longlong()
            _configure_fn(
                lib,
                "goated_bytes_Repeat",
                [
                    ctypes.c_char_p,
                    ctypes.c_longlong,
                    ctypes.c_longlong,
                    ctypes.POINTER(ctypes.c_longlong),
                ],
                ctypes.c_char_p,
            )
            result = lib.goated_bytes_Repeat(b, len(b), count, ctypes.byref(out_len))
            if result:
                return ctypes.string_at(result, out_len.value)
        except Exception:
            pass

    if count < 0:
        raise ValueError("negative Repeat count")
    return b * count


def Replace(s: bytes, old: bytes, new: bytes, n: int) -> bytes:
    """Returns s with the first n non-overlapping instances of old replaced by new."""
    if is_library_available():
        try:
            lib = get_lib()
            out_len = ctypes.c_longlong()
            _configure_fn(
                lib,
                "goated_bytes_Replace",
                [
                    ctypes.c_char_p,
                    ctypes.c_longlong,
                    ctypes.c_char_p,
                    ctypes.c_longlong,
                    ctypes.c_char_p,
                    ctypes.c_longlong,
                    ctypes.c_longlong,
                    ctypes.POINTER(ctypes.c_longlong),
                ],
                ctypes.c_char_p,
            )
            result = lib.goated_bytes_Replace(
                s, len(s), old, len(old), new, len(new), n, ctypes.byref(out_len)
            )
            if result:
                return ctypes.string_at(result, out_len.value)
        except Exception:
            pass

    if n < 0:
        return s.replace(old, new)
    return s.replace(old, new, n)


def ReplaceAll(s: bytes, old: bytes, new: bytes) -> bytes:
    """Returns s with all non-overlapping instances of old replaced by new."""
    return Replace(s, old, new, -1)


def Split(s: bytes, sep: bytes) -> list[bytes]:
    """Slices s into all substrings separated by sep."""
    if sep == b"":
        return [bytes([b]) for b in s]
    return s.split(sep)


def SplitN(s: bytes, sep: bytes, n: int) -> list[bytes]:
    """Slices s into substrings separated by sep, with at most n elements."""
    if n == 0:
        return []
    if n < 0:
        return Split(s, sep)
    if sep == b"":
        result = [bytes([b]) for b in s[: n - 1]]
        if len(s) >= n:
            result.append(s[n - 1 :])
        return result
    return s.split(sep, n - 1)


def SplitAfter(s: bytes, sep: bytes) -> list[bytes]:
    """Slices s into all substrings after each instance of sep."""
    if sep == b"":
        return [bytes([b]) for b in s]
    parts = s.split(sep)
    result = []
    for _i, part in enumerate(parts[:-1]):
        result.append(part + sep)
    if parts:
        result.append(parts[-1])
    return result


def SplitAfterN(s: bytes, sep: bytes, n: int) -> list[bytes]:
    """Slices s into substrings after each instance of sep, with at most n elements."""
    if n == 0:
        return []
    if n < 0:
        return SplitAfter(s, sep)

    result = []
    remaining = s
    count = 0

    while count < n - 1 and sep in remaining:
        idx = remaining.find(sep)
        result.append(remaining[: idx + len(sep)])
        remaining = remaining[idx + len(sep) :]
        count += 1

    if remaining or count < n:
        result.append(remaining)

    return result


def Join(s: list[bytes], sep: bytes) -> bytes:
    """Concatenates the elements of s to create a new byte slice, with sep between elements."""
    return sep.join(s)


def Fields(s: bytes) -> list[bytes]:
    """Splits s around each instance of one or more consecutive white space characters."""
    return s.split()


def Clone(b: bytes) -> bytes:
    """Returns a copy of b."""
    return bytes(b)
