"""GOATED - Go stdlib for Python.

Write Python-like code. Get Go speeds.

This package exposes Go's standard library to Python through high-performance
FFI bindings. It provides three API styles:

1. Direct mapping (goated.std.*) - Go function names preserved
2. Pythonic wrappers (goated.pythonic.*) - snake_case, native returns
3. Drop-in replacements (goated.drop_in.*) - stdlib-compatible API

Concurrency:
    # Async channels (asyncio integration)
    from goated import Channel, go, select

    # Sync goroutines (Go-style concurrency)
    from goated.runtime import go, WaitGroup, Chan, GoGroup
    # Or: from goated.std.goroutine import ...

Example:
    >>> from goated.std import strings
    >>> strings.Split("a,b,c", ",").to_list()
    ['a', 'b', 'c']

    >>> from goated import Ok, Err
    >>> from goated.pythonic import strconv
    >>> match strconv.parse_int("42", base=10):
    ...     case Ok(v): print(f"Got {v}")
    ...     case Err(e): print(f"Error: {e}")
    Got 42

"""

__version__ = "0.1.0"
__author__ = "Goated Contributors"

# Core types - always available
from goated.channel import Channel, ChannelClosed, SelectCase, SelectOp, go, select
from goated.result import Err, GoError, Ok, Result, is_err, is_ok

# Runtime management - expose key functions at top level
from goated.runtime import (
    get_runtime,
    is_free_threaded,
    runtime_stats,
    shutdown_runtime,
)
from goated.types import GoMap, GoSlice, GoString

__all__ = [
    # Version
    "__version__",
    # Result types
    "Ok",
    "Err",
    "Result",
    "GoError",
    "is_ok",
    "is_err",
    # Go types
    "GoSlice",
    "GoString",
    "GoMap",
    # Async Concurrency (asyncio)
    "Channel",
    "ChannelClosed",
    "select",
    "go",
    "SelectCase",
    "SelectOp",
    # Runtime management
    "is_free_threaded",
    "get_runtime",
    "shutdown_runtime",
    "runtime_stats",
]
