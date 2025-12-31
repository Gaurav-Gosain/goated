package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"math"
)


//export goated_math_Abs
func goated_math_Abs(x C.double) C.double {
	result := math.Abs(float64(x))
	return C.double(result)
}

//export goated_math_Acos
func goated_math_Acos(x C.double) C.double {
	result := math.Acos(float64(x))
	return C.double(result)
}

//export goated_math_Acosh
func goated_math_Acosh(x C.double) C.double {
	result := math.Acosh(float64(x))
	return C.double(result)
}

//export goated_math_Asin
func goated_math_Asin(x C.double) C.double {
	result := math.Asin(float64(x))
	return C.double(result)
}

//export goated_math_Asinh
func goated_math_Asinh(x C.double) C.double {
	result := math.Asinh(float64(x))
	return C.double(result)
}

//export goated_math_Atan
func goated_math_Atan(x C.double) C.double {
	result := math.Atan(float64(x))
	return C.double(result)
}

//export goated_math_Atan2
func goated_math_Atan2(y C.double, x C.double) C.double {
	result := math.Atan2(float64(y), float64(x))
	return C.double(result)
}

//export goated_math_Atanh
func goated_math_Atanh(x C.double) C.double {
	result := math.Atanh(float64(x))
	return C.double(result)
}

//export goated_math_Cbrt
func goated_math_Cbrt(x C.double) C.double {
	result := math.Cbrt(float64(x))
	return C.double(result)
}

//export goated_math_Ceil
func goated_math_Ceil(x C.double) C.double {
	result := math.Ceil(float64(x))
	return C.double(result)
}

//export goated_math_Copysign
func goated_math_Copysign(f C.double, sign C.double) C.double {
	result := math.Copysign(float64(f), float64(sign))
	return C.double(result)
}

//export goated_math_Cos
func goated_math_Cos(x C.double) C.double {
	result := math.Cos(float64(x))
	return C.double(result)
}

//export goated_math_Cosh
func goated_math_Cosh(x C.double) C.double {
	result := math.Cosh(float64(x))
	return C.double(result)
}

//export goated_math_Dim
func goated_math_Dim(x C.double, y C.double) C.double {
	result := math.Dim(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_Erf
func goated_math_Erf(x C.double) C.double {
	result := math.Erf(float64(x))
	return C.double(result)
}

//export goated_math_Erfc
func goated_math_Erfc(x C.double) C.double {
	result := math.Erfc(float64(x))
	return C.double(result)
}

//export goated_math_Erfcinv
func goated_math_Erfcinv(x C.double) C.double {
	result := math.Erfcinv(float64(x))
	return C.double(result)
}

//export goated_math_Erfinv
func goated_math_Erfinv(x C.double) C.double {
	result := math.Erfinv(float64(x))
	return C.double(result)
}

//export goated_math_Exp
func goated_math_Exp(x C.double) C.double {
	result := math.Exp(float64(x))
	return C.double(result)
}

//export goated_math_Exp2
func goated_math_Exp2(x C.double) C.double {
	result := math.Exp2(float64(x))
	return C.double(result)
}

//export goated_math_Expm1
func goated_math_Expm1(x C.double) C.double {
	result := math.Expm1(float64(x))
	return C.double(result)
}

//export goated_math_FMA
func goated_math_FMA(x C.double, y C.double, z C.double) C.double {
	result := math.FMA(float64(x), float64(y), float64(z))
	return C.double(result)
}

//export goated_math_Float32bits
func goated_math_Float32bits(f C.float) C.uint {
	result := math.Float32bits(float32(f))
	return C.uint(result)
}

//export goated_math_Float32frombits
func goated_math_Float32frombits(b C.uint) C.float {
	result := math.Float32frombits(uint32(b))
	return C.float(result)
}

//export goated_math_Float64bits
func goated_math_Float64bits(f C.double) C.ulonglong {
	result := math.Float64bits(float64(f))
	return C.ulonglong(result)
}

//export goated_math_Float64frombits
func goated_math_Float64frombits(b C.ulonglong) C.double {
	result := math.Float64frombits(uint64(b))
	return C.double(result)
}

//export goated_math_Floor
func goated_math_Floor(x C.double) C.double {
	result := math.Floor(float64(x))
	return C.double(result)
}

//export goated_math_Gamma
func goated_math_Gamma(x C.double) C.double {
	result := math.Gamma(float64(x))
	return C.double(result)
}

//export goated_math_Hypot
func goated_math_Hypot(p C.double, q C.double) C.double {
	result := math.Hypot(float64(p), float64(q))
	return C.double(result)
}

//export goated_math_Ilogb
func goated_math_Ilogb(x C.double) C.longlong {
	result := math.Ilogb(float64(x))
	return C.longlong(result)
}

//export goated_math_Inf
func goated_math_Inf(sign C.longlong) C.double {
	result := math.Inf(int(sign))
	return C.double(result)
}

//export goated_math_IsInf
func goated_math_IsInf(f C.double, sign C.longlong) C.bool {
	result := math.IsInf(float64(f), int(sign))
	return C.bool(result)
}

//export goated_math_IsNaN
func goated_math_IsNaN(f C.double) C.bool {
	result := math.IsNaN(float64(f))
	return C.bool(result)
}

//export goated_math_J0
func goated_math_J0(x C.double) C.double {
	result := math.J0(float64(x))
	return C.double(result)
}

//export goated_math_J1
func goated_math_J1(x C.double) C.double {
	result := math.J1(float64(x))
	return C.double(result)
}

//export goated_math_Jn
func goated_math_Jn(n C.longlong, x C.double) C.double {
	result := math.Jn(int(n), float64(x))
	return C.double(result)
}

//export goated_math_Ldexp
func goated_math_Ldexp(frac C.double, exp C.longlong) C.double {
	result := math.Ldexp(float64(frac), int(exp))
	return C.double(result)
}

//export goated_math_Log
func goated_math_Log(x C.double) C.double {
	result := math.Log(float64(x))
	return C.double(result)
}

//export goated_math_Log10
func goated_math_Log10(x C.double) C.double {
	result := math.Log10(float64(x))
	return C.double(result)
}

//export goated_math_Log1p
func goated_math_Log1p(x C.double) C.double {
	result := math.Log1p(float64(x))
	return C.double(result)
}

//export goated_math_Log2
func goated_math_Log2(x C.double) C.double {
	result := math.Log2(float64(x))
	return C.double(result)
}

//export goated_math_Logb
func goated_math_Logb(x C.double) C.double {
	result := math.Logb(float64(x))
	return C.double(result)
}

//export goated_math_Max
func goated_math_Max(x C.double, y C.double) C.double {
	result := math.Max(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_Min
func goated_math_Min(x C.double, y C.double) C.double {
	result := math.Min(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_Mod
func goated_math_Mod(x C.double, y C.double) C.double {
	result := math.Mod(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_NaN
func goated_math_NaN() C.double {
	result := math.NaN()
	return C.double(result)
}

//export goated_math_Nextafter
func goated_math_Nextafter(x C.double, y C.double) C.double {
	result := math.Nextafter(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_Nextafter32
func goated_math_Nextafter32(x C.float, y C.float) C.float {
	result := math.Nextafter32(float32(x), float32(y))
	return C.float(result)
}

//export goated_math_Pow
func goated_math_Pow(x C.double, y C.double) C.double {
	result := math.Pow(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_Pow10
func goated_math_Pow10(n C.longlong) C.double {
	result := math.Pow10(int(n))
	return C.double(result)
}

//export goated_math_Remainder
func goated_math_Remainder(x C.double, y C.double) C.double {
	result := math.Remainder(float64(x), float64(y))
	return C.double(result)
}

//export goated_math_Round
func goated_math_Round(x C.double) C.double {
	result := math.Round(float64(x))
	return C.double(result)
}

//export goated_math_RoundToEven
func goated_math_RoundToEven(x C.double) C.double {
	result := math.RoundToEven(float64(x))
	return C.double(result)
}

//export goated_math_Signbit
func goated_math_Signbit(x C.double) C.bool {
	result := math.Signbit(float64(x))
	return C.bool(result)
}

//export goated_math_Sin
func goated_math_Sin(x C.double) C.double {
	result := math.Sin(float64(x))
	return C.double(result)
}

//export goated_math_Sinh
func goated_math_Sinh(x C.double) C.double {
	result := math.Sinh(float64(x))
	return C.double(result)
}

//export goated_math_Sqrt
func goated_math_Sqrt(x C.double) C.double {
	result := math.Sqrt(float64(x))
	return C.double(result)
}

//export goated_math_Tan
func goated_math_Tan(x C.double) C.double {
	result := math.Tan(float64(x))
	return C.double(result)
}

//export goated_math_Tanh
func goated_math_Tanh(x C.double) C.double {
	result := math.Tanh(float64(x))
	return C.double(result)
}

//export goated_math_Trunc
func goated_math_Trunc(x C.double) C.double {
	result := math.Trunc(float64(x))
	return C.double(result)
}

//export goated_math_Y0
func goated_math_Y0(x C.double) C.double {
	result := math.Y0(float64(x))
	return C.double(result)
}

//export goated_math_Y1
func goated_math_Y1(x C.double) C.double {
	result := math.Y1(float64(x))
	return C.double(result)
}

//export goated_math_Yn
func goated_math_Yn(n C.longlong, x C.double) C.double {
	result := math.Yn(int(n), float64(x))
	return C.double(result)
}

