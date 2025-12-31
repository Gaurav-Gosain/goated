package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"unicode/utf8"
)


//export goated_utf8_FullRuneInString
func goated_utf8_FullRuneInString(s *C.char) C.bool {
	result := utf8.FullRuneInString(C.GoString(s))
	return C.bool(result)
}

//export goated_utf8_RuneCountInString
func goated_utf8_RuneCountInString(s *C.char) C.longlong {
	result := utf8.RuneCountInString(C.GoString(s))
	return C.longlong(result)
}

//export goated_utf8_RuneLen
func goated_utf8_RuneLen(r C.int) C.longlong {
	result := utf8.RuneLen(rune(r))
	return C.longlong(result)
}

//export goated_utf8_RuneStart
func goated_utf8_RuneStart(b C.uchar) C.bool {
	result := utf8.RuneStart(byte(b))
	return C.bool(result)
}

//export goated_utf8_ValidRune
func goated_utf8_ValidRune(r C.int) C.bool {
	result := utf8.ValidRune(rune(r))
	return C.bool(result)
}

//export goated_utf8_ValidString
func goated_utf8_ValidString(s *C.char) C.bool {
	result := utf8.ValidString(C.GoString(s))
	return C.bool(result)
}

