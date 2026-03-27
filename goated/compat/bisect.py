"""Drop-in replacement for Python's bisect module.

Python's bisect module is already C-optimized and extremely fast.
This module is provided for completeness of the compat namespace and
passes all operations through to Python's bisect.

Usage:
    from goated.compat import bisect
    index = bisect.bisect_left([1, 2, 4, 5], 3)
    bisect.insort(sorted_list, new_item)
"""

from __future__ import annotations

# Re-export everything from Python's bisect module
from bisect import (  # noqa: F401
    bisect,
    bisect_left,
    bisect_right,
    insort,
    insort_left,
    insort_right,
)

__all__ = [
    "bisect",
    "bisect_left",
    "bisect_right",
    "insort",
    "insort_left",
    "insort_right",
]
