package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"net/url"
)

//export goated_url_parse
func goated_url_parse(rawurl *C.char, errOut **C.char) C.ulonglong {
	u, err := url.Parse(C.GoString(rawurl))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.ulonglong(newHandle(u))
}

//export goated_url_query_escape
func goated_url_query_escape(s *C.char) *C.char {
	return C.CString(url.QueryEscape(C.GoString(s)))
}

//export goated_url_query_unescape
func goated_url_query_unescape(s *C.char, errOut **C.char) *C.char {
	result, err := url.QueryUnescape(C.GoString(s))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}

//export goated_url_path_escape
func goated_url_path_escape(s *C.char) *C.char {
	return C.CString(url.PathEscape(C.GoString(s)))
}

//export goated_url_path_unescape
func goated_url_path_unescape(s *C.char, errOut **C.char) *C.char {
	result, err := url.PathUnescape(C.GoString(s))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}
