package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"strconv"
)

// ParseInt result structure
type parseIntResult struct {
	value int64
	err   string
}

// ParseFloat result structure
type parseFloatResult struct {
	value float64
	err   string
}

//export goated_strconv_Atoi
func goated_strconv_Atoi(s *C.char, errOut **C.char) C.longlong {
	result, err := strconv.Atoi(C.GoString(s))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.longlong(result)
}

//export goated_strconv_Itoa
func goated_strconv_Itoa(i C.longlong) *C.char {
	return C.CString(strconv.Itoa(int(i)))
}

//export goated_strconv_ParseInt
func goated_strconv_ParseInt(s *C.char, base C.int, bitSize C.int, errOut **C.char) C.longlong {
	result, err := strconv.ParseInt(C.GoString(s), int(base), int(bitSize))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.longlong(result)
}

//export goated_strconv_ParseUint
func goated_strconv_ParseUint(s *C.char, base C.int, bitSize C.int, errOut **C.char) C.ulonglong {
	result, err := strconv.ParseUint(C.GoString(s), int(base), int(bitSize))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.ulonglong(result)
}

//export goated_strconv_ParseFloat
func goated_strconv_ParseFloat(s *C.char, bitSize C.int, errOut **C.char) C.double {
	result, err := strconv.ParseFloat(C.GoString(s), int(bitSize))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.double(result)
}

//export goated_strconv_ParseBool
func goated_strconv_ParseBool(s *C.char, errOut **C.char) C.bool {
	result, err := strconv.ParseBool(C.GoString(s))
	if err != nil {
		*errOut = C.CString(err.Error())
		return false
	}
	*errOut = nil
	return C.bool(result)
}

//export goated_strconv_FormatInt
func goated_strconv_FormatInt(i C.longlong, base C.int) *C.char {
	return C.CString(strconv.FormatInt(int64(i), int(base)))
}

//export goated_strconv_FormatUint
func goated_strconv_FormatUint(i C.ulonglong, base C.int) *C.char {
	return C.CString(strconv.FormatUint(uint64(i), int(base)))
}

//export goated_strconv_FormatFloat
func goated_strconv_FormatFloat(f C.double, fmt C.char, prec C.int, bitSize C.int) *C.char {
	return C.CString(strconv.FormatFloat(float64(f), byte(fmt), int(prec), int(bitSize)))
}

//export goated_strconv_FormatBool
func goated_strconv_FormatBool(b C.bool) *C.char {
	return C.CString(strconv.FormatBool(bool(b)))
}

//export goated_strconv_Quote
func goated_strconv_Quote(s *C.char) *C.char {
	return C.CString(strconv.Quote(C.GoString(s)))
}

//export goated_strconv_QuoteToASCII
func goated_strconv_QuoteToASCII(s *C.char) *C.char {
	return C.CString(strconv.QuoteToASCII(C.GoString(s)))
}

//export goated_strconv_Unquote
func goated_strconv_Unquote(s *C.char, errOut **C.char) *C.char {
	result, err := strconv.Unquote(C.GoString(s))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}
