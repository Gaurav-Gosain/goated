package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"html"
)

//export goated_html_escape_string
func goated_html_escape_string(s *C.char) *C.char {
	return C.CString(html.EscapeString(C.GoString(s)))
}

//export goated_html_unescape_string
func goated_html_unescape_string(s *C.char) *C.char {
	return C.CString(html.UnescapeString(C.GoString(s)))
}
