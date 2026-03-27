"""Drop-in replacement for Python's heapq module.

Uses Go sort for nlargest/nsmallest on large iterables.
All other operations (heappush, heappop, heapify) pass through to Python's
C-optimized heapq which operates on Python lists in-place.

Usage:
    from goated.compat import heapq
    heap = []
    heapq.heappush(heap, 5)
    heapq.heappush(heap, 3)
    smallest = heapq.heappop(heap)
    top5 = heapq.nlargest(5, data)
"""

from __future__ import annotations

import ctypes
import heapq as _heapq

# Re-export in-place operations unchanged (these modify Python lists directly)
from heapq import (  # noqa: F401
    heapify,
    heappop,
    heappush,
    heappushpop,
    heapreplace,
    merge,
)
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 10000  # Only use Go sort for very large iterables
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_sort_float64s.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
        lib.goated_sort_float64s.restype = None
        _lib_setup = True
    except Exception:
        pass


def _go_sort_floats(values: list[float]) -> list[float]:
    """Sort floats using Go's sort.Float64s for large arrays."""
    _setup_lib()
    if not _lib_setup:
        return sorted(values)
    try:
        lib = get_lib().lib
        n = len(values)
        arr = (ctypes.c_double * n)(*values)
        lib.goated_sort_float64s(arr, ctypes.c_int(n))
        return list(arr)
    except Exception:
        return sorted(values)


def nlargest(n: int, iterable: Any, key: Any = None) -> list[Any]:
    """Find the n largest elements in a dataset.

    Uses Go sort for large iterables of numbers without a key function.
    """
    if key is not None:
        return _heapq.nlargest(n, iterable, key)
    items = list(iterable)
    if len(items) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _heapq.nlargest(n, items)
    # Try Go sort for numeric data
    try:
        float_items = [float(x) for x in items]
        sorted_items = _go_sort_floats(float_items)
        # nlargest returns in descending order
        return sorted_items[-n:][::-1] if n <= len(sorted_items) else sorted_items[::-1]
    except (TypeError, ValueError):
        return _heapq.nlargest(n, items)


def nsmallest(n: int, iterable: Any, key: Any = None) -> list[Any]:
    """Find the n smallest elements in a dataset.

    Uses Go sort for large iterables of numbers without a key function.
    """
    if key is not None:
        return _heapq.nsmallest(n, iterable, key)
    items = list(iterable)
    if len(items) < _GO_THRESHOLD or not _USE_GO_LIB:
        return _heapq.nsmallest(n, items)
    # Try Go sort for numeric data
    try:
        float_items = [float(x) for x in items]
        sorted_items = _go_sort_floats(float_items)
        return sorted_items[:n]
    except (TypeError, ValueError):
        return _heapq.nsmallest(n, items)


__all__ = [
    "heappush",
    "heappop",
    "heappushpop",
    "heapreplace",
    "heapify",
    "merge",
    "nlargest",
    "nsmallest",
]
