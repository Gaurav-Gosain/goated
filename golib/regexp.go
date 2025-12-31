package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"regexp"
)


//export goated_regexp_MatchString
func goated_regexp_MatchString(pattern *C.char, s *C.char, errOut **C.char) C.bool {
	result, err := regexp.MatchString(C.GoString(pattern), C.GoString(s))
	if err != nil {
		*errOut = C.CString(err.Error())
		return false
	}
	*errOut = nil
	return C.bool(result)
}

//export goated_regexp_QuoteMeta
func goated_regexp_QuoteMeta(s *C.char) *C.char {
	result := regexp.QuoteMeta(C.GoString(s))
	return C.CString(result)
}

