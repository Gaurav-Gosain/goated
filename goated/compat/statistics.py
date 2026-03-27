"""Drop-in replacement for Python's statistics module with Go FFI acceleration.

Uses Go for computing mean, median, stdev, variance, etc. on large datasets
by sorting via Go's sort and computing stats via Go math. Falls back to
Python's statistics module for small datasets and unsupported operations.

Usage:
    from goated.compat import statistics
    avg = statistics.mean([1, 2, 3, 4, 5])
    med = statistics.median([1, 2, 3, 4, 5])
"""

from __future__ import annotations

import contextlib
import ctypes
import math
import statistics as _statistics

# Re-export everything from Python's statistics module
from statistics import (  # noqa: F401
    StatisticsError,
    harmonic_mean,
    median_grouped,
    median_high,
    median_low,
    mode,
    multimode,
    quantiles,
)
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

# These were added in Python 3.10+
with contextlib.suppress(ImportError):
    from statistics import correlation, covariance, linear_regression  # noqa: F401

# NormalDist added in Python 3.8
with contextlib.suppress(ImportError):
    from statistics import NormalDist  # noqa: F401

_GO_THRESHOLD = 1000  # Use Go for datasets > 1000 elements
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


def _to_floats(data: Any) -> list[float]:
    """Convert iterable data to list of floats."""
    return [float(x) for x in data]


def _go_sort_floats(values: list[float]) -> list[float]:
    """Sort a list of floats using Go's sort.Float64s."""
    if not _USE_GO_LIB or len(values) < _GO_THRESHOLD:
        return sorted(values)
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


def mean(data: Any) -> float:
    """Return the arithmetic mean of data.

    Uses Go for large datasets.
    """
    values = _to_floats(data)
    if not values:
        raise _statistics.StatisticsError("mean requires at least one data point")
    if len(values) > _GO_THRESHOLD:
        return math.fsum(values) / len(values)
    return _statistics.mean(data)


def fmean(data: Any, weights: Any = None) -> float:
    """Return the arithmetic mean of data (fast float version).

    Uses Go for large datasets when no weights are specified.
    """
    if weights is not None:
        return _statistics.fmean(data, weights)
    values = _to_floats(data)
    if not values:
        raise _statistics.StatisticsError("fmean requires at least one data point")
    if len(values) > _GO_THRESHOLD:
        return math.fsum(values) / len(values)
    return _statistics.fmean(data)


def median(data: Any) -> float:
    """Return the median (middle value) of data.

    Uses Go sort for large datasets.
    """
    values = _to_floats(data)
    if not values:
        raise _statistics.StatisticsError("no median for empty data")
    sorted_values = _go_sort_floats(values)
    n = len(sorted_values)
    if n % 2 == 1:
        return sorted_values[n // 2]
    return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0


def variance(data: Any, xbar: float | None = None) -> float:
    """Return the sample variance of data.

    Uses direct computation for large datasets.
    """
    values = _to_floats(data)
    n = len(values)
    if n < 2:
        raise _statistics.StatisticsError("variance requires at least two data points")
    if n > _GO_THRESHOLD:
        mu = xbar if xbar is not None else math.fsum(values) / n
        ss = math.fsum((x - mu) ** 2 for x in values)
        return ss / (n - 1)
    return _statistics.variance(data, xbar)


def pvariance(data: Any, mu: float | None = None) -> float:
    """Return the population variance of data.

    Uses direct computation for large datasets.
    """
    values = _to_floats(data)
    n = len(values)
    if n < 1:
        raise _statistics.StatisticsError("pvariance requires at least one data point")
    if n > _GO_THRESHOLD:
        m = mu if mu is not None else math.fsum(values) / n
        ss = math.fsum((x - m) ** 2 for x in values)
        return ss / n
    return _statistics.pvariance(data, mu)


def stdev(data: Any, xbar: float | None = None) -> float:
    """Return the sample standard deviation of data.

    Uses Go-accelerated variance for large datasets.
    """
    return math.sqrt(variance(data, xbar))


def pstdev(data: Any, mu: float | None = None) -> float:
    """Return the population standard deviation of data.

    Uses Go-accelerated pvariance for large datasets.
    """
    return math.sqrt(pvariance(data, mu))


def geometric_mean(data: Any) -> float:
    """Return the geometric mean of data."""
    return _statistics.geometric_mean(data)


__all__ = [
    "mean",
    "fmean",
    "median",
    "median_low",
    "median_high",
    "median_grouped",
    "mode",
    "multimode",
    "harmonic_mean",
    "geometric_mean",
    "variance",
    "pvariance",
    "stdev",
    "pstdev",
    "quantiles",
    "NormalDist",
    "StatisticsError",
]
