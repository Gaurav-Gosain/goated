package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"unicode"
)


//export goated_unicode_IsControl
func goated_unicode_IsControl(r C.int) C.bool {
	result := unicode.IsControl(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsDigit
func goated_unicode_IsDigit(r C.int) C.bool {
	result := unicode.IsDigit(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsGraphic
func goated_unicode_IsGraphic(r C.int) C.bool {
	result := unicode.IsGraphic(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsLetter
func goated_unicode_IsLetter(r C.int) C.bool {
	result := unicode.IsLetter(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsLower
func goated_unicode_IsLower(r C.int) C.bool {
	result := unicode.IsLower(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsMark
func goated_unicode_IsMark(r C.int) C.bool {
	result := unicode.IsMark(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsNumber
func goated_unicode_IsNumber(r C.int) C.bool {
	result := unicode.IsNumber(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsPrint
func goated_unicode_IsPrint(r C.int) C.bool {
	result := unicode.IsPrint(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsPunct
func goated_unicode_IsPunct(r C.int) C.bool {
	result := unicode.IsPunct(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsSpace
func goated_unicode_IsSpace(r C.int) C.bool {
	result := unicode.IsSpace(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsSymbol
func goated_unicode_IsSymbol(r C.int) C.bool {
	result := unicode.IsSymbol(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsTitle
func goated_unicode_IsTitle(r C.int) C.bool {
	result := unicode.IsTitle(rune(r))
	return C.bool(result)
}

//export goated_unicode_IsUpper
func goated_unicode_IsUpper(r C.int) C.bool {
	result := unicode.IsUpper(rune(r))
	return C.bool(result)
}

//export goated_unicode_SimpleFold
func goated_unicode_SimpleFold(r C.int) C.int {
	result := unicode.SimpleFold(rune(r))
	return C.int(result)
}

//export goated_unicode_To
func goated_unicode_To(_case C.longlong, r C.int) C.int {
	result := unicode.To(int(_case), rune(r))
	return C.int(result)
}

//export goated_unicode_ToLower
func goated_unicode_ToLower(r C.int) C.int {
	result := unicode.ToLower(rune(r))
	return C.int(result)
}

//export goated_unicode_ToTitle
func goated_unicode_ToTitle(r C.int) C.int {
	result := unicode.ToTitle(rune(r))
	return C.int(result)
}

//export goated_unicode_ToUpper
func goated_unicode_ToUpper(r C.int) C.int {
	result := unicode.ToUpper(rune(r))
	return C.int(result)
}

