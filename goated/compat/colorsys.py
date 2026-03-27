"""Drop-in replacement for Python's colorsys module with Go batch acceleration.

Single conversions use Python directly (Go FFI overhead too high for simple math).
Batch conversions use Go parallel processing for large datasets.

Usage:
    from goated.compat import colorsys
    h, s, v = colorsys.rgb_to_hsv(0.5, 0.3, 0.8)
    results = colorsys.batch_rgb_to_hsv([(0.5, 0.3, 0.8), (1.0, 0.0, 0.0)])
"""

from __future__ import annotations

import colorsys as _colorsys
import ctypes
from collections.abc import Sequence

# Re-export all single-conversion functions from Python's colorsys
from colorsys import (  # noqa: F401
    hls_to_rgb,
    hsv_to_rgb,
    rgb_to_hls,
    rgb_to_hsv,
    rgb_to_yiq,
    yiq_to_rgb,
)

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 100  # Use Go for batches > 100 colors
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_rgb_to_hsv.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
        ]
        lib.goated_rgb_to_hsv.restype = None
        lib.goated_batch_rgb_to_hsv.argtypes = [
            ctypes.POINTER(ctypes.c_double),  # rs
            ctypes.POINTER(ctypes.c_double),  # gs
            ctypes.POINTER(ctypes.c_double),  # bs
            ctypes.c_int,                      # count
            ctypes.POINTER(ctypes.c_double),  # hs
            ctypes.POINTER(ctypes.c_double),  # ss
            ctypes.POINTER(ctypes.c_double),  # vs
        ]
        lib.goated_batch_rgb_to_hsv.restype = None
        _lib_setup = True
    except Exception:
        pass


def batch_rgb_to_hsv(
    colors: Sequence[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    """Convert a batch of RGB colors to HSV. Go-accelerated for large batches.

    This is a goated extension -- not part of Python's colorsys module.

    Args:
        colors: Sequence of (r, g, b) tuples, each in [0.0, 1.0].

    Returns:
        List of (h, s, v) tuples.

    """
    n = len(colors)
    if n < _GO_THRESHOLD or not _USE_GO_LIB:
        return [_colorsys.rgb_to_hsv(r, g, b) for r, g, b in colors]

    # Prefer cffi
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi

            rs = _cffi_ffi.new("double[]", n)
            gs = _cffi_ffi.new("double[]", n)
            bs = _cffi_ffi.new("double[]", n)
            for i, (r, g, b) in enumerate(colors):
                rs[i] = r
                gs[i] = g
                bs[i] = b

            hs = _cffi_ffi.new("double[]", n)
            ss = _cffi_ffi.new("double[]", n)
            vs = _cffi_ffi.new("double[]", n)

            cffi_lib.goated_batch_rgb_to_hsv(rs, gs, bs, n, hs, ss, vs)
            return [(hs[i], ss[i], vs[i]) for i in range(n)]
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            DoubleArray = ctypes.c_double * n

            rs = DoubleArray(*(c[0] for c in colors))
            gs = DoubleArray(*(c[1] for c in colors))
            bs_arr = DoubleArray(*(c[2] for c in colors))

            hs = DoubleArray()
            ss = DoubleArray()
            vs = DoubleArray()

            lib.goated_batch_rgb_to_hsv(rs, gs, bs_arr, n, hs, ss, vs)
            return [(hs[i], ss[i], vs[i]) for i in range(n)]
        except Exception:
            pass

    return [_colorsys.rgb_to_hsv(r, g, b) for r, g, b in colors]


def batch_hsv_to_rgb(
    colors: Sequence[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    """Convert a batch of HSV colors to RGB. Python implementation.

    This is a goated extension -- not part of Python's colorsys module.

    Args:
        colors: Sequence of (h, s, v) tuples.

    Returns:
        List of (r, g, b) tuples.

    """
    return [_colorsys.hsv_to_rgb(h, s, v) for h, s, v in colors]


__all__ = [
    "rgb_to_hsv",
    "hsv_to_rgb",
    "rgb_to_hls",
    "hls_to_rgb",
    "rgb_to_yiq",
    "yiq_to_rgb",
    "batch_rgb_to_hsv",
    "batch_hsv_to_rgb",
]
