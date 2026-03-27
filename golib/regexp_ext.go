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

//export goated_regexp_compile
func goated_regexp_compile(pattern *C.char, errOut **C.char) C.ulonglong {
	re, err := regexp.Compile(C.GoString(pattern))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.ulonglong(newHandle(re))
}

//export goated_regexp_find_string
func goated_regexp_find_string(handle C.ulonglong, s *C.char) *C.char {
	re, ok := getHandle[*regexp.Regexp](uint64(handle))
	if !ok {
		return nil
	}
	result := re.FindString(C.GoString(s))
	return C.CString(result)
}

//export goated_regexp_find_all_string
func goated_regexp_find_all_string(handle C.ulonglong, s *C.char, n C.int) C.ulonglong {
	re, ok := getHandle[*regexp.Regexp](uint64(handle))
	if !ok {
		return 0
	}
	result := re.FindAllString(C.GoString(s), int(n))
	return C.ulonglong(newHandle(result))
}

//export goated_regexp_replace_all_string
func goated_regexp_replace_all_string(handle C.ulonglong, src *C.char, repl *C.char) *C.char {
	re, ok := getHandle[*regexp.Regexp](uint64(handle))
	if !ok {
		return nil
	}
	result := re.ReplaceAllString(C.GoString(src), C.GoString(repl))
	return C.CString(result)
}

//export goated_regexp_split
func goated_regexp_split(handle C.ulonglong, s *C.char, n C.int) C.ulonglong {
	re, ok := getHandle[*regexp.Regexp](uint64(handle))
	if !ok {
		return 0
	}
	result := re.Split(C.GoString(s), int(n))
	return C.ulonglong(newHandle(result))
}

//export goated_regexp_match_string
func goated_regexp_match_string(handle C.ulonglong, s *C.char) C.bool {
	re, ok := getHandle[*regexp.Regexp](uint64(handle))
	if !ok {
		return C.bool(false)
	}
	return C.bool(re.MatchString(C.GoString(s)))
}
