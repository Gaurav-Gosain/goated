"""Go math package bindings - Auto-generated.

This module provides Python bindings for Go's math package.
"""

from __future__ import annotations

import math as _math
import struct

__all__ = [
    "Abs",
    "Acos",
    "Acosh",
    "Asin",
    "Asinh",
    "Atan",
    "Atan2",
    "Atanh",
    "Cbrt",
    "Ceil",
    "Copysign",
    "Cos",
    "Cosh",
    "Dim",
    "Exp",
    "Exp2",
    "Expm1",
    "FMA",
    "Float32bits",
    "Float32frombits",
    "Float64bits",
    "Float64frombits",
    "Floor",
    "Hypot",
    "Ilogb",
    "Inf",
    "IsInf",
    "IsNaN",
    "Ldexp",
    "Log",
    "Log10",
    "Log1p",
    "Log2",
    "Logb",
    "Max",
    "Min",
    "Mod",
    "NaN",
    "Nextafter",
    "Pow",
    "Pow10",
    "Remainder",
    "Round",
    "RoundToEven",
    "Signbit",
    "Sin",
    "Sinh",
    "Sqrt",
    "Tan",
    "Tanh",
    "Trunc",
    # Constants
    "E",
    "Pi",
    "Phi",
    "Sqrt2",
    "SqrtE",
    "SqrtPi",
    "SqrtPhi",
    "Ln2",
    "Log2E",
    "Ln10",
    "Log10E",
    "MaxFloat32",
    "SmallestNonzeroFloat32",
    "MaxFloat64",
    "SmallestNonzeroFloat64",
    "MaxInt",
    "MinInt",
    "MaxInt8",
    "MinInt8",
    "MaxInt16",
    "MinInt16",
    "MaxInt32",
    "MinInt32",
    "MaxInt64",
    "MinInt64",
    "MaxUint",
    "MaxUint8",
    "MaxUint16",
    "MaxUint32",
    "MaxUint64",
]

# Mathematical constants
E = _math.e
Pi = _math.pi
Phi = (1 + _math.sqrt(5)) / 2  # Golden ratio
Sqrt2 = _math.sqrt(2)
SqrtE = _math.sqrt(_math.e)
SqrtPi = _math.sqrt(_math.pi)
SqrtPhi = _math.sqrt(Phi)
Ln2 = _math.log(2)
Log2E = 1 / Ln2
Ln10 = _math.log(10)
Log10E = 1 / Ln10

# Floating-point limits
MaxFloat32 = 3.40282346638528859811704183484516925440e38
SmallestNonzeroFloat32 = 1.401298464324817070923729583289916131280e-45
MaxFloat64 = 1.7976931348623157e308
SmallestNonzeroFloat64 = 5e-324

# Integer limits (Python 3 has arbitrary precision, but Go doesn't)
MaxInt8 = 127
MinInt8 = -128
MaxInt16 = 32767
MinInt16 = -32768
MaxInt32 = 2147483647
MinInt32 = -2147483648
MaxInt64 = 9223372036854775807
MinInt64 = -9223372036854775808
MaxUint8 = 255
MaxUint16 = 65535
MaxUint32 = 4294967295
MaxUint64 = 18446744073709551615
# Platform-dependent (assume 64-bit)
MaxInt = MaxInt64
MinInt = MinInt64
MaxUint = MaxUint64


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")


_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[object], restype: object) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


def Abs(x: float) -> float:
    """Abs returns the absolute value of x.

    Special cases are:

        Abs(±Inf) = +Inf
        Abs(NaN) = NaN
    """
    return _math.fabs(x)


def Acos(x: float) -> float:
    """Acos returns the arccosine, in radians, of x.

    Special case is:

        Acos(x) = NaN if x < -1 or x > 1
    """
    try:
        return _math.acos(x)
    except ValueError:
        return _math.nan


def Acosh(x: float) -> float:
    """Acosh returns the inverse hyperbolic cosine of x.

    Special cases are:

        Acosh(+Inf) = +Inf
        Acosh(x) = NaN if x < 1
        Acosh(NaN) = NaN
    """
    try:
        return _math.acosh(x)
    except ValueError:
        return _math.nan


def Asin(x: float) -> float:
    """Asin returns the arcsine, in radians, of x.

    Special cases are:

        Asin(±0) = ±0
        Asin(x) = NaN if x < -1 or x > 1
    """
    try:
        return _math.asin(x)
    except ValueError:
        return _math.nan


def Asinh(x: float) -> float:
    """Asinh returns the inverse hyperbolic sine of x.

    Special cases are:

        Asinh(±0) = ±0
        Asinh(±Inf) = ±Inf
        Asinh(NaN) = NaN
    """
    return _math.asinh(x)


def Atan(x: float) -> float:
    """Atan returns the arctangent, in radians, of x.

    Special cases are:

        Atan(±0) = ±0
        Atan(±Inf) = ±Pi/2
    """
    return _math.atan(x)


def Atan2(y: float, x: float) -> float:
    """Atan2 returns the arc tangent of y/x, using
    the signs of the two to determine the quadrant
    of the return value.
    """
    return _math.atan2(y, x)


def Atanh(x: float) -> float:
    """Atanh returns the inverse hyperbolic tangent of x.

    Special cases are:

        Atanh(1) = +Inf
        Atanh(±0) = ±0
        Atanh(-1) = -Inf
        Atanh(x) = NaN if x < -1 or x > 1
        Atanh(NaN) = NaN
    """
    try:
        return _math.atanh(x)
    except ValueError:
        if x == 1:
            return _math.inf
        elif x == -1:
            return -_math.inf
        return _math.nan


def Cbrt(x: float) -> float:
    """Cbrt returns the cube root of x.

    Special cases are:

        Cbrt(±0) = ±0
        Cbrt(±Inf) = ±Inf
        Cbrt(NaN) = NaN
    """
    # Python's pow doesn't handle negative numbers for fractional powers
    if x < 0:
        return -(_math.pow(-x, 1 / 3))
    return _math.pow(x, 1 / 3) if x != 0 else 0.0


def Ceil(x: float) -> float:
    """Ceil returns the least integer value greater than or equal to x.

    Special cases are:

        Ceil(±0) = ±0
        Ceil(±Inf) = ±Inf
        Ceil(NaN) = NaN
    """
    return _math.ceil(x)


def Copysign(f: float, sign: float) -> float:
    """Copysign returns a value with the magnitude of f
    and the sign of sign.
    """
    return _math.copysign(f, sign)


def Cos(x: float) -> float:
    """Cos returns the cosine of the radian argument x.

    Special cases are:

        Cos(±Inf) = NaN
        Cos(NaN) = NaN
    """
    if _math.isinf(x):
        return _math.nan
    return _math.cos(x)


def Cosh(x: float) -> float:
    """Cosh returns the hyperbolic cosine of x.

    Special cases are:

        Cosh(±0) = 1
        Cosh(±Inf) = +Inf
        Cosh(NaN) = NaN
    """
    return _math.cosh(x)


def Dim(x: float, y: float) -> float:
    """Dim returns the maximum of x-y or 0.

    Special cases are:

        Dim(+Inf, +Inf) = NaN
        Dim(-Inf, -Inf) = NaN
        Dim(x, NaN) = Dim(NaN, x) = NaN
    """
    if _math.isnan(x) or _math.isnan(y):
        return _math.nan
    if _math.isinf(x) and _math.isinf(y) and (x > 0) == (y > 0):
        return _math.nan
    return max(x - y, 0.0)


def Exp(x: float) -> float:
    """Exp returns e**x, the base-e exponential of x.

    Special cases are:

        Exp(+Inf) = +Inf
        Exp(NaN) = NaN
    """
    return _math.exp(x)


def Exp2(x: float) -> float:
    """Exp2 returns 2**x, the base-2 exponential of x.

    Special cases are the same as [Exp].
    """
    return _math.pow(2, x)


def Expm1(x: float) -> float:
    """Expm1 returns e**x - 1, the base-e exponential of x minus 1.
    It is more accurate than [Exp](x) - 1 when x is near zero.
    """
    return _math.expm1(x)


def FMA(x: float, y: float, z: float) -> float:
    """FMA returns x * y + z, computed with only one rounding.
    (That is, FMA returns the fused multiply-add of x, y, and z.).
    """
    return _math.fma(x, y, z) if hasattr(_math, "fma") else x * y + z


def Float32bits(f: float) -> int:
    """Float32bits returns the IEEE 754 binary representation of f,
    with the sign bit of f and the result in the same bit position.
    """
    result: int = struct.unpack(">I", struct.pack(">f", f))[0]
    return result


def Float32frombits(b: int) -> float:
    """Float32frombits returns the floating-point number corresponding
    to the IEEE 754 binary representation b.
    """
    result: float = struct.unpack(">f", struct.pack(">I", b & 0xFFFFFFFF))[0]
    return result


def Float64bits(f: float) -> int:
    """Float64bits returns the IEEE 754 binary representation of f,
    with the sign bit of f and the result in the same bit position.
    """
    result: int = struct.unpack(">Q", struct.pack(">d", f))[0]
    return result


def Float64frombits(b: int) -> float:
    """Float64frombits returns the floating-point number corresponding
    to the IEEE 754 binary representation b.
    """
    result: float = struct.unpack(">d", struct.pack(">Q", b & 0xFFFFFFFFFFFFFFFF))[0]
    return result


def Floor(x: float) -> float:
    """Floor returns the greatest integer value less than or equal to x.

    Special cases are:

        Floor(±0) = ±0
        Floor(±Inf) = ±Inf
        Floor(NaN) = NaN
    """
    return _math.floor(x)


def Hypot(p: float, q: float) -> float:
    """Hypot returns [Sqrt](p*p + q*q), taking care to avoid
    unnecessary overflow and underflow.
    """
    return _math.hypot(p, q)


def Ilogb(x: float) -> int:
    """Ilogb returns the binary exponent of x as an integer.

    Special cases are:

        Ilogb(±Inf) = MaxInt32
        Ilogb(0) = MinInt32
        Ilogb(NaN) = MaxInt32
    """
    if _math.isnan(x) or _math.isinf(x):
        return MaxInt32
    if x == 0:
        return MinInt32
    # frexp returns (m, e) where x = m * 2**e and 0.5 <= |m| < 1
    # ilogb is e - 1
    _, e = _math.frexp(x)
    return e - 1


def Inf(sign: int) -> float:
    """Inf returns positive infinity if sign >= 0, negative infinity if sign < 0."""
    if sign >= 0:
        return _math.inf
    return -_math.inf


def IsInf(f: float, sign: int) -> bool:
    """IsInf reports whether f is an infinity, according to sign.
    If sign > 0, IsInf reports whether f is positive infinity.
    If sign < 0, IsInf reports whether f is negative infinity.
    If sign == 0, IsInf reports whether f is either infinity.
    """
    if sign > 0:
        return f == _math.inf
    elif sign < 0:
        return f == -_math.inf
    return _math.isinf(f)


def IsNaN(f: float) -> bool:
    """IsNaN reports whether f is an IEEE 754 "not-a-number" value."""
    return _math.isnan(f)


def Ldexp(frac: float, exp: int) -> float:
    """Ldexp is the inverse of [Frexp].
    It returns frac × 2**exp.
    """
    return _math.ldexp(frac, exp)


def Log(x: float) -> float:
    """Log returns the natural logarithm of x.

    Special cases are:

        Log(+Inf) = +Inf
        Log(0) = -Inf
        Log(x < 0) = NaN
        Log(NaN) = NaN
    """
    try:
        return _math.log(x)
    except ValueError:
        if x == 0:
            return -_math.inf
        return _math.nan


def Log10(x: float) -> float:
    """Log10 returns the decimal logarithm of x.
    The special cases are the same as for [Log].
    """
    try:
        return _math.log10(x)
    except ValueError:
        if x == 0:
            return -_math.inf
        return _math.nan


def Log1p(x: float) -> float:
    """Log1p returns the natural logarithm of 1 plus its argument x.
    It is more accurate than [Log](1 + x) when x is near zero.
    """
    try:
        return _math.log1p(x)
    except ValueError:
        if x == -1:
            return -_math.inf
        return _math.nan


def Log2(x: float) -> float:
    """Log2 returns the binary logarithm of x.
    The special cases are the same as for [Log].
    """
    try:
        return _math.log2(x)
    except ValueError:
        if x == 0:
            return -_math.inf
        return _math.nan


def Logb(x: float) -> float:
    """Logb returns the binary exponent of x.

    Special cases are:

        Logb(±Inf) = +Inf
        Logb(0) = -Inf
        Logb(NaN) = NaN
    """
    if _math.isnan(x):
        return _math.nan
    if _math.isinf(x):
        return _math.inf
    if x == 0:
        return -_math.inf
    _, e = _math.frexp(x)
    return float(e - 1)


def Max(x: float, y: float) -> float:
    """Max returns the larger of x or y.

    Special cases are:

        Max(x, +Inf) = Max(+Inf, x) = +Inf
        Max(x, NaN) = Max(NaN, x) = NaN
        Max(+0, ±0) = Max(±0, +0) = +0
        Max(-0, -0) = -0
    """
    if _math.isnan(x) or _math.isnan(y):
        return _math.nan
    # Handle signed zeros
    if x == 0 and y == 0:
        # Check if either is positive zero
        if _math.copysign(1, x) > 0 or _math.copysign(1, y) > 0:
            return 0.0
        return -0.0
    return max(x, y)


def Min(x: float, y: float) -> float:
    """Min returns the smaller of x or y.

    Special cases are:

        Min(x, -Inf) = Min(-Inf, x) = -Inf
        Min(x, NaN) = Min(NaN, x) = NaN
        Min(-0, ±0) = Min(±0, -0) = -0
    """
    if _math.isnan(x) or _math.isnan(y):
        return _math.nan
    # Handle signed zeros
    if x == 0 and y == 0:
        # Check if either is negative zero
        if _math.copysign(1, x) < 0 or _math.copysign(1, y) < 0:
            return -0.0
        return 0.0
    return min(x, y)


def Mod(x: float, y: float) -> float:
    """Mod returns the floating-point remainder of x/y.
    The magnitude of the result is less than y and its
    sign agrees with that of x.
    """
    if _math.isnan(x) or _math.isnan(y) or _math.isinf(x) or y == 0:
        return _math.nan
    if _math.isinf(y):
        return x
    return _math.fmod(x, y)


def NaN() -> float:
    """NaN returns an IEEE 754 "not-a-number" value."""
    return _math.nan


def Nextafter(x: float, y: float) -> float:
    """Nextafter returns the next representable float64 value after x towards y.

    Special cases are:

        Nextafter(x, x)   = x
        Nextafter(NaN, y) = NaN
        Nextafter(x, NaN) = NaN
    """
    return _math.nextafter(x, y)


def Pow(x: float, y: float) -> float:
    """Pow returns x**y, the base-x exponential of y."""
    try:
        return _math.pow(x, y)
    except (ValueError, OverflowError):
        # Handle special cases
        if _math.isnan(x) or _math.isnan(y):
            return _math.nan
        return _math.inf


def Pow10(n: int) -> float:
    """Pow10 returns 10**n, the base-10 exponential of n."""
    try:
        return _math.pow(10, n)
    except OverflowError:
        if n > 0:
            return _math.inf
        return 0.0


def Remainder(x: float, y: float) -> float:
    """Remainder returns the IEEE 754 floating-point remainder of x/y."""
    if _math.isnan(x) or _math.isnan(y) or _math.isinf(x) or y == 0:
        return _math.nan
    if _math.isinf(y):
        return x
    return _math.remainder(x, y)


def Round(x: float) -> float:
    """Round returns the nearest integer, rounding half away from zero."""
    if _math.isnan(x) or _math.isinf(x):
        return x
    # Python's round uses banker's rounding, but Go rounds half away from zero
    if x >= 0:
        return _math.floor(x + 0.5)
    return _math.ceil(x - 0.5)


def RoundToEven(x: float) -> float:
    """RoundToEven returns the nearest integer, rounding ties to even."""
    if _math.isnan(x) or _math.isinf(x):
        return x
    return float(round(x))


def Signbit(x: float) -> bool:
    """Signbit reports whether x is negative or negative zero."""
    return _math.copysign(1, x) < 0


def Sin(x: float) -> float:
    """Sin returns the sine of the radian argument x.

    Special cases are:

        Sin(±0) = ±0
        Sin(±Inf) = NaN
        Sin(NaN) = NaN
    """
    if _math.isinf(x):
        return _math.nan
    return _math.sin(x)


def Sinh(x: float) -> float:
    """Sinh returns the hyperbolic sine of x.

    Special cases are:

        Sinh(±0) = ±0
        Sinh(±Inf) = ±Inf
        Sinh(NaN) = NaN
    """
    return _math.sinh(x)


def Sqrt(x: float) -> float:
    """Sqrt returns the square root of x.

    Special cases are:

        Sqrt(+Inf) = +Inf
        Sqrt(±0) = ±0
        Sqrt(x < 0) = NaN
        Sqrt(NaN) = NaN
    """
    try:
        return _math.sqrt(x)
    except ValueError:
        return _math.nan


def Tan(x: float) -> float:
    """Tan returns the tangent of the radian argument x.

    Special cases are:

        Tan(±0) = ±0
        Tan(±Inf) = NaN
        Tan(NaN) = NaN
    """
    if _math.isinf(x):
        return _math.nan
    return _math.tan(x)


def Tanh(x: float) -> float:
    """Tanh returns the hyperbolic tangent of x.

    Special cases are:

        Tanh(±0) = ±0
        Tanh(±Inf) = ±1
        Tanh(NaN) = NaN
    """
    return _math.tanh(x)


def Trunc(x: float) -> float:
    """Trunc returns the integer value of x.

    Special cases are:

        Trunc(±0) = ±0
        Trunc(±Inf) = ±Inf
        Trunc(NaN) = NaN
    """
    return _math.trunc(x)
