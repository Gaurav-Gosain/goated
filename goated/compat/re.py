r"""Drop-in replacement for Python's re module.

This module provides the same API as Python's re module.
It wraps Go's regexp package (RE2) for pattern matching when available.

Note: Go's RE2 has some differences from Python's PCRE:
- RE2 guarantees linear time matching
- Some features like backreferences are not supported in RE2

Usage:
    from goated.compat import re

    # Same API as stdlib re
    pattern = re.compile(r'\\d+')
    match = pattern.search('hello 123 world')
    matches = re.findall(r'\\w+', 'hello world')
"""

from __future__ import annotations

# Re-export everything from Python's re module
from re import (
    ASCII,
    DEBUG,
    DOTALL,
    IGNORECASE,
    LOCALE,
    MULTILINE,
    UNICODE,
    VERBOSE,
    # Flags
    A,
    I,
    L,
    M,
    Match,
    Pattern,
    S,
    U,
    X,
    compile,
    error,
    escape,
    findall,
    finditer,
    fullmatch,
    match,
    purge,
    search,
    split,
    sub,
    subn,
)

# NOFLAG was added in Python 3.11
try:
    from re import NOFLAG  # type: ignore[attr-defined]
except ImportError:
    NOFLAG = 0

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
