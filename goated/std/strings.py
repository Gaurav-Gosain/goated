"""Go strings package bindings.
Uses Go library when available, falls back to Python.
"""

from __future__ import annotations

from collections.abc import Callable

from goated._core import _USE_GO_LIB, get_lib

__all__ = [
    "Contains",
    "ContainsAny",
    "ContainsRune",
    "Count",
    "EqualFold",
    "HasPrefix",
    "HasSuffix",
    "Index",
    "IndexAny",
    "IndexByte",
    "IndexRune",
    "LastIndex",
    "LastIndexAny",
    "LastIndexByte",
    "Split",
    "SplitN",
    "SplitAfter",
    "SplitAfterN",
    "Join",
    "Fields",
    "FieldsFunc",
    "ToLower",
    "ToUpper",
    "ToTitle",
    "Title",
    "Repeat",
    "Replace",
    "ReplaceAll",
    "Trim",
    "TrimLeft",
    "TrimRight",
    "TrimSpace",
    "TrimPrefix",
    "TrimSuffix",
    "Builder",
]


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")


# Get library reference once at module load (if available)
_lib = get_lib() if _USE_GO_LIB else None


def Contains(s: str, substr: str) -> bool:
    """Reports whether substr is within s."""
    if _lib:
        return bool(_lib.goated_strings_Contains(_encode(s), _encode(substr)))
    return substr in s


def ContainsAny(s: str, chars: str) -> bool:
    """Reports whether any Unicode code points in chars are within s."""
    if _lib:
        return bool(_lib.goated_strings_ContainsAny(_encode(s), _encode(chars)))
    return any(c in s for c in chars)


def ContainsRune(s: str, r: str) -> bool:
    """Reports whether the Unicode code point r is within s."""
    if len(r) != 1:
        raise ValueError("ContainsRune requires a single character")
    return r in s


def Count(s: str, substr: str) -> int:
    """Counts the number of non-overlapping instances of substr in s."""
    if _lib:
        return int(_lib.goated_strings_Count(_encode(s), _encode(substr)))
    if substr == "":
        return len(s) + 1
    return s.count(substr)


def EqualFold(s: str, t: str) -> bool:
    """Reports whether s and t are equal under Unicode case-folding."""
    if _lib:
        return bool(_lib.goated_strings_EqualFold(_encode(s), _encode(t)))
    return s.casefold() == t.casefold()


def HasPrefix(s: str, prefix: str) -> bool:
    """Tests whether the string s begins with prefix."""
    if _lib:
        return bool(_lib.goated_strings_HasPrefix(_encode(s), _encode(prefix)))
    return s.startswith(prefix)


def HasSuffix(s: str, suffix: str) -> bool:
    """Tests whether the string s ends with suffix."""
    if _lib:
        return bool(_lib.goated_strings_HasSuffix(_encode(s), _encode(suffix)))
    return s.endswith(suffix)


def Index(s: str, substr: str) -> int:
    """Returns the index of the first instance of substr in s, or -1."""
    if _lib:
        return int(_lib.goated_strings_Index(_encode(s), _encode(substr)))
    return s.find(substr)


def IndexAny(s: str, chars: str) -> int:
    """Returns the index of the first instance of any char from chars in s."""
    if _lib:
        return int(_lib.goated_strings_IndexAny(_encode(s), _encode(chars)))
    for i, c in enumerate(s):
        if c in chars:
            return i
    return -1


def IndexByte(s: str, c: str) -> int:
    """Returns the index of the first instance of c in s, or -1."""
    if len(c) != 1:
        raise ValueError("IndexByte requires a single character")
    if _lib:
        return int(_lib.goated_strings_IndexByte(_encode(s), ord(c[0])))
    return s.find(c)


def IndexRune(s: str, r: str) -> int:
    """Returns the index of the first instance of r in s, or -1."""
    return s.find(r)


def LastIndex(s: str, substr: str) -> int:
    """Returns the index of the last instance of substr in s, or -1."""
    if _lib:
        return int(_lib.goated_strings_LastIndex(_encode(s), _encode(substr)))
    return s.rfind(substr)


def LastIndexAny(s: str, chars: str) -> int:
    """Returns the index of the last instance of any char from chars in s."""
    if _lib:
        return int(_lib.goated_strings_LastIndexAny(_encode(s), _encode(chars)))
    for i in range(len(s) - 1, -1, -1):
        if s[i] in chars:
            return i
    return -1


def LastIndexByte(s: str, c: str) -> int:
    """Returns the index of the last instance of c in s, or -1."""
    if _lib:
        return int(_lib.goated_strings_LastIndexByte(_encode(s), ord(c[0]) if c else 0))
    return s.rfind(c)


def Split(s: str, sep: str) -> list[str]:
    """Slices s into all substrings separated by sep."""
    if sep == "":
        return list(s)
    return s.split(sep)


def SplitN(s: str, sep: str, n: int) -> list[str]:
    """Slices s into substrings separated by sep, at most n substrings."""
    if n == 0:
        return []
    if n < 0:
        return s.split(sep)
    return s.split(sep, n - 1)


def SplitAfter(s: str, sep: str) -> list[str]:
    """Slices s into all substrings after each instance of sep."""
    if not sep:
        return list(s)
    result = []
    start = 0
    while True:
        idx = s.find(sep, start)
        if idx < 0:
            result.append(s[start:])
            break
        result.append(s[start : idx + len(sep)])
        start = idx + len(sep)
    return result


def SplitAfterN(s: str, sep: str, n: int) -> list[str]:
    """Slices s into substrings after each instance of sep, max n parts."""
    if n == 0:
        return []
    if n < 0:
        return SplitAfter(s, sep)
    result = []
    start = 0
    for _ in range(n - 1):
        idx = s.find(sep, start)
        if idx < 0:
            break
        result.append(s[start : idx + len(sep)])
        start = idx + len(sep)
    result.append(s[start:])
    return result


def Join(elems: list[str], sep: str) -> str:
    """Concatenates the elements of elems to create a single string."""
    return sep.join(elems)


def Fields(s: str) -> list[str]:
    """Splits the string s around whitespace."""
    return s.split()


def FieldsFunc(s: str, f: Callable[[str], bool]) -> list[str]:
    """Splits s at each run of code points c satisfying f(c)."""
    result = []
    current: list[str] = []
    for c in s:
        if f(c):
            if current:
                result.append("".join(current))
                current = []
        else:
            current.append(c)
    if current:
        result.append("".join(current))
    return result


def ToLower(s: str) -> str:
    """Returns s with all Unicode letters mapped to lower case."""
    if _lib:
        return _decode(_lib.goated_strings_ToLower(_encode(s)))
    return s.lower()


def ToUpper(s: str) -> str:
    """Returns s with all Unicode letters mapped to upper case."""
    if _lib:
        return _decode(_lib.goated_strings_ToUpper(_encode(s)))
    return s.upper()


def ToTitle(s: str) -> str:
    """Returns s with all Unicode letters mapped to title case."""
    if _lib:
        return _decode(_lib.goated_strings_ToTitle(_encode(s)))
    return s.upper()


def Title(s: str) -> str:
    """Returns s with all Unicode letters that begin words mapped to title case."""
    if _lib:
        return _decode(_lib.goated_strings_Title(_encode(s)))
    return s.title()


def Repeat(s: str, count: int) -> str:
    """Returns a new string consisting of count copies of s."""
    if count < 0:
        raise ValueError("negative Repeat count")
    if _lib:
        result = _lib.goated_strings_Repeat(_encode(s), count)
        return _decode(result) if result else ""
    return s * count


def Replace(s: str, old: str, new: str, n: int) -> str:
    """Returns s with the first n instances of old replaced by new."""
    if _lib:
        return _decode(_lib.goated_strings_Replace(_encode(s), _encode(old), _encode(new), n))
    if n < 0:
        return s.replace(old, new)
    return s.replace(old, new, n)


def ReplaceAll(s: str, old: str, new: str) -> str:
    """Returns s with all instances of old replaced by new."""
    if _lib:
        return _decode(_lib.goated_strings_ReplaceAll(_encode(s), _encode(old), _encode(new)))
    return s.replace(old, new)


def Trim(s: str, cutset: str) -> str:
    """Returns s with leading and trailing chars from cutset removed."""
    if _lib:
        return _decode(_lib.goated_strings_Trim(_encode(s), _encode(cutset)))
    return s.strip(cutset)


def TrimLeft(s: str, cutset: str) -> str:
    """Returns s with leading chars from cutset removed."""
    if _lib:
        return _decode(_lib.goated_strings_TrimLeft(_encode(s), _encode(cutset)))
    return s.lstrip(cutset)


def TrimRight(s: str, cutset: str) -> str:
    """Returns s with trailing chars from cutset removed."""
    if _lib:
        return _decode(_lib.goated_strings_TrimRight(_encode(s), _encode(cutset)))
    return s.rstrip(cutset)


def TrimSpace(s: str) -> str:
    """Returns s with leading and trailing white space removed."""
    if _lib:
        return _decode(_lib.goated_strings_TrimSpace(_encode(s)))
    return s.strip()


def TrimPrefix(s: str, prefix: str) -> str:
    """Returns s without the provided leading prefix string."""
    if _lib:
        return _decode(_lib.goated_strings_TrimPrefix(_encode(s), _encode(prefix)))
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def TrimSuffix(s: str, suffix: str) -> str:
    """Returns s without the provided trailing suffix string."""
    if _lib:
        return _decode(_lib.goated_strings_TrimSuffix(_encode(s), _encode(suffix)))
    if suffix and s.endswith(suffix):
        return s[: -len(suffix)]
    return s


class Builder:
    """A Builder is used to efficiently build a string using Write methods."""

    __slots__ = ("_parts",)

    def __init__(self) -> None:
        self._parts: list[str] = []

    def WriteString(self, s: str) -> int:
        self._parts.append(s)
        return len(s)

    def WriteByte(self, c: int) -> None:
        self._parts.append(chr(c))

    def WriteRune(self, r: str) -> int:
        self._parts.append(r)
        return len(r.encode("utf-8"))

    def String(self) -> str:
        return "".join(self._parts)

    def Len(self) -> int:
        return sum(len(p.encode("utf-8")) for p in self._parts)

    def Cap(self) -> int:
        return self.Len()

    def Reset(self) -> None:
        self._parts.clear()

    def Grow(self, n: int) -> None:
        pass

    def __str__(self) -> str:
        return self.String()

    def __repr__(self) -> str:
        return f"Builder({self.String()!r})"

    def __len__(self) -> int:
        return self.Len()
