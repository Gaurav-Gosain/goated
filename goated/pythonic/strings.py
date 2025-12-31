"""Go strings package bindings - Pythonic style.

This module wraps Go's strings package with Python-friendly naming (snake_case)
and native return types. Functions behave like their Go counterparts but feel
more natural in Python code.

Example:
    >>> from goated.pythonic import strings
    >>>
    >>> strings.split("a,b,c", ",")
    ['a', 'b', 'c']
    >>>
    >>> strings.to_upper("hello")
    'HELLO'
    >>>
    >>> strings.contains("hello world", "world")
    True

"""

from __future__ import annotations

from collections.abc import Callable

from goated.std import strings as go_strings

__all__ = [
    "contains",
    "contains_any",
    "contains_rune",
    "count",
    "equal_fold",
    "has_prefix",
    "has_suffix",
    "index",
    "index_any",
    "index_byte",
    "index_rune",
    "last_index",
    "last_index_any",
    "last_index_byte",
    "split",
    "split_n",
    "split_after",
    "split_after_n",
    "join",
    "fields",
    "fields_func",
    "to_lower",
    "to_upper",
    "to_title",
    "title",
    "repeat",
    "replace",
    "replace_all",
    "trim",
    "trim_left",
    "trim_right",
    "trim_space",
    "trim_prefix",
    "trim_suffix",
    "Builder",
]


def contains(s: str, substr: str) -> bool:
    """Check if substr is within s."""
    return go_strings.Contains(s, substr)


def contains_any(s: str, chars: str) -> bool:
    """Check if any character from chars is in s."""
    return go_strings.ContainsAny(s, chars)


def contains_rune(s: str, r: str) -> bool:
    """Check if character r is in s."""
    return go_strings.ContainsRune(s, r)


def count(s: str, substr: str) -> int:
    """Count non-overlapping instances of substr in s."""
    return go_strings.Count(s, substr)


def equal_fold(s: str, t: str) -> bool:
    """Check if strings are equal under Unicode case-folding."""
    return go_strings.EqualFold(s, t)


def has_prefix(s: str, prefix: str) -> bool:
    """Check if s starts with prefix."""
    return go_strings.HasPrefix(s, prefix)


def has_suffix(s: str, suffix: str) -> bool:
    """Check if s ends with suffix."""
    return go_strings.HasSuffix(s, suffix)


def index(s: str, substr: str) -> int:
    """Return index of first occurrence of substr, or -1."""
    return go_strings.Index(s, substr)


def index_any(s: str, chars: str) -> int:
    """Return index of first character from chars in s, or -1."""
    return go_strings.IndexAny(s, chars)


def index_byte(s: str, c: str) -> int:
    """Return index of first occurrence of byte c, or -1."""
    return go_strings.IndexByte(s, c)


def index_rune(s: str, r: str) -> int:
    """Return index of first occurrence of rune r, or -1."""
    return go_strings.IndexRune(s, r)


def last_index(s: str, substr: str) -> int:
    """Return index of last occurrence of substr, or -1."""
    return go_strings.LastIndex(s, substr)


def last_index_any(s: str, chars: str) -> int:
    """Return index of last character from chars in s, or -1."""
    return go_strings.LastIndexAny(s, chars)


def last_index_byte(s: str, c: str) -> int:
    """Return index of last occurrence of byte c, or -1."""
    return go_strings.LastIndexByte(s, c)


def split(s: str, sep: str) -> list[str]:
    """Split s by separator sep."""
    result = go_strings.Split(s, sep)
    if isinstance(result, list):
        return result
    return result.to_list()


def split_n(s: str, sep: str, n: int) -> list[str]:
    """Split s by sep into at most n substrings."""
    return go_strings.SplitN(s, sep, n)


def split_after(s: str, sep: str) -> list[str]:
    """Split s after each occurrence of sep."""
    return go_strings.SplitAfter(s, sep)


def split_after_n(s: str, sep: str, n: int) -> list[str]:
    """Split s after each occurrence of sep, into at most n substrings."""
    return go_strings.SplitAfterN(s, sep, n)


def join(elems: list[str], sep: str) -> str:
    """Join elements with separator."""
    return go_strings.Join(elems, sep)


def fields(s: str) -> list[str]:
    """Split s around whitespace."""
    return go_strings.Fields(s)


def fields_func(s: str, f: Callable[[str], bool]) -> list[str]:
    """Split s where f returns True."""
    return go_strings.FieldsFunc(s, f)


def to_lower(s: str) -> str:
    """Convert s to lowercase."""
    return go_strings.ToLower(s)


def to_upper(s: str) -> str:
    """Convert s to uppercase."""
    return go_strings.ToUpper(s)


def to_title(s: str) -> str:
    """Convert s to title case."""
    return go_strings.ToTitle(s)


def title(s: str) -> str:
    """Convert s to title case (deprecated, use to_title)."""
    return go_strings.Title(s)


def repeat(s: str, count: int) -> str:
    """Return s repeated count times."""
    return go_strings.Repeat(s, count)


def replace(s: str, old: str, new: str, n: int = -1) -> str:
    """Replace first n occurrences of old with new (-1 for all)."""
    return go_strings.Replace(s, old, new, n)


def replace_all(s: str, old: str, new: str) -> str:
    """Replace all occurrences of old with new."""
    return go_strings.ReplaceAll(s, old, new)


def trim(s: str, cutset: str) -> str:
    """Remove leading and trailing characters in cutset."""
    return go_strings.Trim(s, cutset)


def trim_left(s: str, cutset: str) -> str:
    """Remove leading characters in cutset."""
    return go_strings.TrimLeft(s, cutset)


def trim_right(s: str, cutset: str) -> str:
    """Remove trailing characters in cutset."""
    return go_strings.TrimRight(s, cutset)


def trim_space(s: str) -> str:
    """Remove leading and trailing whitespace."""
    return go_strings.TrimSpace(s)


def trim_prefix(s: str, prefix: str) -> str:
    """Remove prefix from s if present."""
    return go_strings.TrimPrefix(s, prefix)


def trim_suffix(s: str, suffix: str) -> str:
    """Remove suffix from s if present."""
    return go_strings.TrimSuffix(s, suffix)


Builder = go_strings.Builder
