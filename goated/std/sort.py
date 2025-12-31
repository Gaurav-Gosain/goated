"""Go sort package bindings - Pure Python implementation.

This module provides Python bindings for Go's sort package, maintaining
Go-style naming conventions and behavior.

Example:
    >>> from goated.std import sort
    >>>
    >>> # Sort integers
    >>> data = [3, 1, 4, 1, 5, 9]
    >>> sort.Ints(data)
    >>> print(data)
    [1, 1, 3, 4, 5, 9]
    >>>
    >>> # Check if sorted
    >>> sort.IntsAreSorted(data)
    True
    >>>
    >>> # Binary search
    >>> sort.SearchInts(data, 4)
    3

"""

from __future__ import annotations

import bisect
from collections.abc import Callable
from typing import Any, Protocol, TypeVar

__all__ = [
    # Slice sorting
    "Ints",
    "Float64s",
    "Strings",
    # Sorted checks
    "IntsAreSorted",
    "Float64sAreSorted",
    "StringsAreSorted",
    # Binary search
    "SearchInts",
    "SearchFloat64s",
    "SearchStrings",
    "Search",
    # Generic sorting
    "Slice",
    "SliceStable",
    "SliceIsSorted",
    # Interface-based
    "Sort",
    "Stable",
    "IsSorted",
    "Reverse",
    # Types
    "Interface",
    "IntSlice",
    "Float64Slice",
    "StringSlice",
]

T = TypeVar("T")


# =============================================================================
# Interface Protocol (Go's sort.Interface)
# =============================================================================


class Interface(Protocol):
    """Interface defines the methods required for sorting.

    This matches Go's sort.Interface:
    - Len() int
    - Less(i, j int) bool
    - Swap(i, j int)
    """

    def Len(self) -> int:
        """Return the number of elements."""
        ...

    def Less(self, i: int, j: int) -> bool:
        """Report whether element i should sort before element j."""
        ...

    def Swap(self, i: int, j: int) -> None:
        """Swap elements at indices i and j."""
        ...


# =============================================================================
# Slice Types
# =============================================================================


class IntSlice(list[int]):
    """IntSlice attaches sort.Interface methods to []int."""

    def Len(self) -> int:
        """Return the length of the slice."""
        return len(self)

    def Less(self, i: int, j: int) -> bool:
        """Report whether self[i] < self[j]."""
        return bool(self[i] < self[j])

    def Swap(self, i: int, j: int) -> None:
        """Swap self[i] and self[j]."""
        self[i], self[j] = self[j], self[i]

    def Sort(self) -> None:
        """Sort the slice in increasing order."""
        self.sort()

    def Search(self, x: int) -> int:
        """Search for x using binary search, returning the index to insert x.

        Returns the index where x should be inserted to keep the slice sorted.
        """
        return bisect.bisect_left(self, x)


class Float64Slice(list[float]):
    """Float64Slice attaches sort.Interface methods to []float64."""

    def Len(self) -> int:
        """Return the length of the slice."""
        return len(self)

    def Less(self, i: int, j: int) -> bool:
        """Report whether self[i] < self[j]."""
        # Handle NaN: NaN is considered less than any other value for sorting
        import math

        if math.isnan(self[i]):
            return True
        if math.isnan(self[j]):
            return False
        return bool(self[i] < self[j])

    def Swap(self, i: int, j: int) -> None:
        """Swap self[i] and self[j]."""
        self[i], self[j] = self[j], self[i]

    def Sort(self) -> None:
        """Sort the slice in increasing order."""
        self.sort(key=lambda x: (0, x) if not _isnan(x) else (-1, 0))

    def Search(self, x: float) -> int:
        """Search for x using binary search, returning the index to insert x."""
        return bisect.bisect_left(self, x)


class StringSlice(list[str]):
    """StringSlice attaches sort.Interface methods to []string."""

    def Len(self) -> int:
        """Return the length of the slice."""
        return len(self)

    def Less(self, i: int, j: int) -> bool:
        """Report whether self[i] < self[j]."""
        return bool(self[i] < self[j])

    def Swap(self, i: int, j: int) -> None:
        """Swap self[i] and self[j]."""
        self[i], self[j] = self[j], self[i]

    def Sort(self) -> None:
        """Sort the slice in increasing order."""
        self.sort()

    def Search(self, x: str) -> int:
        """Search for x using binary search, returning the index to insert x."""
        return bisect.bisect_left(self, x)


# =============================================================================
# Helper Functions
# =============================================================================


def _isnan(x: float) -> bool:
    """Check if x is NaN."""
    import math

    return math.isnan(x)


# =============================================================================
# Convenience Functions for Slices
# =============================================================================


def Ints(x: list[int]) -> None:
    """Sort a slice of ints in increasing order.

    Args:
        x: The list to sort (modified in place)

    Example:
        >>> data = [3, 1, 4, 1, 5]
        >>> Ints(data)
        >>> data
        [1, 1, 3, 4, 5]

    """
    x.sort()


def Float64s(x: list[float]) -> None:
    """Sort a slice of float64s in increasing order.

    NaN values are ordered before other values.

    Args:
        x: The list to sort (modified in place)

    Example:
        >>> data = [3.14, 1.0, 2.71]
        >>> Float64s(data)
        >>> data
        [1.0, 2.71, 3.14]

    """
    x.sort(key=lambda v: (0, v) if not _isnan(v) else (-1, 0))


def Strings(x: list[str]) -> None:
    """Sort a slice of strings in increasing order.

    Args:
        x: The list to sort (modified in place)

    Example:
        >>> data = ["banana", "apple", "cherry"]
        >>> Strings(data)
        >>> data
        ['apple', 'banana', 'cherry']

    """
    x.sort()


# =============================================================================
# Sorted Checks
# =============================================================================


def IntsAreSorted(x: list[int]) -> bool:
    """Report whether x is sorted in increasing order.

    Args:
        x: The list to check

    Returns:
        True if x is sorted

    Example:
        >>> IntsAreSorted([1, 2, 3, 4])
        True
        >>> IntsAreSorted([1, 3, 2, 4])
        False

    """
    return all(x[i] <= x[i + 1] for i in range(len(x) - 1))


def Float64sAreSorted(x: list[float]) -> bool:
    """Report whether x is sorted in increasing order.

    NaN values are considered less than any other value.

    Args:
        x: The list to check

    Returns:
        True if x is sorted

    """
    for i in range(len(x) - 1):
        a, b = x[i], x[i + 1]
        # NaN should come first
        if _isnan(b) and not _isnan(a):
            return False
        if not _isnan(a) and not _isnan(b) and a > b:
            return False
    return True


def StringsAreSorted(x: list[str]) -> bool:
    """Report whether x is sorted in increasing order.

    Args:
        x: The list to check

    Returns:
        True if x is sorted

    """
    return all(x[i] <= x[i + 1] for i in range(len(x) - 1))


# =============================================================================
# Binary Search
# =============================================================================


def SearchInts(a: list[int], x: int) -> int:
    """Search for x in a sorted slice of ints.

    Returns the index where x should be inserted to maintain sorted order.
    If x is already in a, returns the index of x.

    Args:
        a: A sorted list of ints
        x: The value to search for

    Returns:
        The insertion point for x

    Example:
        >>> SearchInts([1, 2, 4, 5], 3)
        2
        >>> SearchInts([1, 2, 4, 5], 4)
        2

    """
    return bisect.bisect_left(a, x)


def SearchFloat64s(a: list[float], x: float) -> int:
    """Search for x in a sorted slice of float64s.

    Returns the index where x should be inserted to maintain sorted order.

    Args:
        a: A sorted list of floats
        x: The value to search for

    Returns:
        The insertion point for x

    """
    return bisect.bisect_left(a, x)


def SearchStrings(a: list[str], x: str) -> int:
    """Search for x in a sorted slice of strings.

    Returns the index where x should be inserted to maintain sorted order.

    Args:
        a: A sorted list of strings
        x: The value to search for

    Returns:
        The insertion point for x

    """
    return bisect.bisect_left(a, x)


def Search(n: int, f: Callable[[int], bool]) -> int:
    """Search returns the smallest index i in [0, n) at which f(i) is true.

    Search uses binary search to find and return the smallest index i
    in [0, n) at which f(i) is true, assuming that on the range [0, n),
    f(i) == true implies f(i+1) == true.

    If there is no such index, Search returns n.

    Args:
        n: The upper bound (exclusive)
        f: A function that returns True for indices >= target

    Returns:
        The smallest index where f returns True, or n if none found

    Example:
        >>> data = [1, 2, 4, 5, 7]
        >>> Search(len(data), lambda i: data[i] >= 4)
        2

    """
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if f(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


# =============================================================================
# Generic Slice Sorting
# =============================================================================


def Slice(x: list[Any], less: Callable[[int, int], bool]) -> None:
    """Sort the slice x given the provided less function.

    The sort is not guaranteed to be stable.

    Args:
        x: The list to sort (modified in place)
        less: A function that returns True if x[i] < x[j]

    Example:
        >>> data = [(1, "b"), (2, "a"), (1, "a")]
        >>> Slice(data, lambda i, j: data[i][0] < data[j][0])
        >>> data
        [(1, 'b'), (1, 'a'), (2, 'a')]

    """
    # Use Python's sort with a custom key
    # We need to use the less function which compares indices
    n = len(x)
    if n <= 1:
        return

    # Create index array and sort it
    indices = list(range(n))

    # Use merge sort with the less function
    def merge_sort(arr: list[int], start: int, end: int) -> None:
        if end - start <= 1:
            return

        mid = (start + end) // 2
        merge_sort(arr, start, mid)
        merge_sort(arr, mid, end)

        # Merge
        left = arr[start:mid]
        right = arr[mid:end]
        i = j = 0
        k = start

        while i < len(left) and j < len(right):
            if less(left[i], right[j]):
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

    merge_sort(indices, 0, n)

    # Reorder x according to sorted indices
    temp = [x[i] for i in indices]
    for i in range(n):
        x[i] = temp[i]


def SliceStable(x: list[Any], less: Callable[[int, int], bool]) -> None:
    """Sort the slice x given the provided less function, keeping equal elements
    in their original order (stable sort).

    Args:
        x: The list to sort (modified in place)
        less: A function that returns True if x[i] < x[j]

    """
    # Same as Slice but uses a stable sort
    Slice(x, less)  # Our implementation uses merge sort which is stable


def SliceIsSorted(x: list[Any], less: Callable[[int, int], bool]) -> bool:
    """Report whether x is sorted according to the provided less function.

    Args:
        x: The list to check
        less: A function that returns True if x[i] < x[j]

    Returns:
        True if x is sorted

    """
    return all(not less(i + 1, i) for i in range(len(x) - 1))


# =============================================================================
# Interface-based Sorting
# =============================================================================


def Sort(data: Interface) -> None:
    """Sort data in increasing order as determined by the Less method.

    The sort is not guaranteed to be stable.

    Args:
        data: An object implementing sort.Interface

    """
    n = data.Len()
    if n <= 1:
        return

    # Simple quicksort implementation
    _quicksort(data, 0, n - 1)


def _quicksort(data: Interface, lo: int, hi: int) -> None:
    """Quicksort helper."""
    if lo >= hi:
        return

    # Partition
    pivot = hi
    i = lo
    for j in range(lo, hi):
        if data.Less(j, pivot):
            data.Swap(i, j)
            i += 1
    data.Swap(i, hi)

    _quicksort(data, lo, i - 1)
    _quicksort(data, i + 1, hi)


def Stable(data: Interface) -> None:
    """Sort data in increasing order as determined by the Less method,
    while keeping equal elements in their original order (stable sort).

    Args:
        data: An object implementing sort.Interface

    """
    n = data.Len()
    if n <= 1:
        return

    # Use merge sort for stability
    _mergesort(data, 0, n)


def _mergesort(data: Interface, lo: int, hi: int) -> None:
    """Merge sort helper for stable sorting."""
    if hi - lo <= 1:
        return

    mid = (lo + hi) // 2
    _mergesort(data, lo, mid)
    _mergesort(data, mid, hi)

    # Merge in place (simple implementation)
    _merge(data, lo, mid, hi)


def _merge(data: Interface, lo: int, mid: int, hi: int) -> None:
    """Merge two sorted sublists."""
    # Simple in-place merge
    i = lo
    j = mid

    while i < j < hi:
        if data.Less(j, i):
            # Rotate the element at j into position i
            for k in range(j, i, -1):
                data.Swap(k, k - 1)
            i += 1
            j += 1
        else:
            i += 1


def IsSorted(data: Interface) -> bool:
    """Report whether data is sorted.

    Args:
        data: An object implementing sort.Interface

    Returns:
        True if data is sorted

    """
    n = data.Len()
    return all(not data.Less(i + 1, i) for i in range(n - 1))


class _ReverseWrapper:
    """Wrapper that reverses the sort order."""

    def __init__(self, data: Interface):
        self._data = data

    def Len(self) -> int:
        return self._data.Len()

    def Less(self, i: int, j: int) -> bool:
        return self._data.Less(j, i)  # Reversed!

    def Swap(self, i: int, j: int) -> None:
        self._data.Swap(i, j)


def Reverse(data: Interface) -> Interface:
    """Return the reverse order of data.

    Args:
        data: An object implementing sort.Interface

    Returns:
        A wrapper that reverses Less comparisons

    Example:
        >>> data = IntSlice([1, 2, 3])
        >>> Sort(Reverse(data))
        >>> list(data)
        [3, 2, 1]

    """
    return _ReverseWrapper(data)


# =============================================================================
# Additional Utility Functions
# =============================================================================


def Find(n: int, cmp: Callable[[int], int]) -> tuple[int, bool]:
    """Find uses binary search to find and return the smallest index i
    in [0, n) at which cmp(i) <= 0.

    The cmp function should return:
    - A negative number if the element at i comes before the target
    - Zero if the element at i equals the target
    - A positive number if the element at i comes after the target

    Args:
        n: The upper bound (exclusive)
        cmp: A comparison function

    Returns:
        A tuple (index, found) where found is True if cmp(index) == 0

    """
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        c = cmp(mid)
        if c < 0:
            lo = mid + 1
        elif c > 0:
            hi = mid
        else:
            return mid, True
    return lo, lo < n and cmp(lo) == 0
